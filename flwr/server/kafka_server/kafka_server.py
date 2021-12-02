# Copyright 2020 Adap GmbH. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Implements utility function to create a grpc server."""
from queue import Queue
import sys
import time
import json
from typing import Callable, Any, Mapping
from flwr.common import KAFKA_MAX_SIZE, StoppableThread
from flwr.common.logger import log
from flwr.proto.transport_pb2 import ClientMessage, ServerMessage
from flwr.proto import transport_pb2 as flwr_dot_proto_dot_transport__pb2
from logging import INFO, DEBUG
from flwr.server.client_manager import ClientManager, SimpleClientManager
from flwr.server.kafka_server import flower_service_servicer as fss
from kafka_consumer.consumer import MsgReceiver
from kafka_producer.producer import MsgSender
# from flwr.server.app import SERVER_TOPIC


def start_kafka_receiver(
    client_manager: ClientManager,
    server_address: str,
    max_concurrent_workers: int = 1000,
    max_message_length: int = KAFKA_MAX_SIZE,
    topic_name = None
) :
    """Create kafka server and return registered FlowerServiceServicer instance.

    If used in a main function server.wait_for_termination(timeout=None)
    should be called as otherwise the server will immediately stop.

    Parameters
    ----------
    client_manager : ClientManager
        Instance of ClientManager
    server_address : str
        Server address in the form of HOST:PORT e.g. "[::]:8080"
    max_concurrent_workers : int
        Set the maximum number of clients you want the server to process
        before returning RESOURCE_EXHAUSTED status (default: 1000)
    max_message_length : int
        Maximum message length that the server can send or receive.
        Int valued in bytes. -1 means unlimited. (default: GRPC_MAX_MESSAGE_LENGTH)

    Returns
    -------
    server : kafka receiver
        An instance of a receiver which is already started
    """

    server = KafkaServer(server_address=server_address, 
                         max_message_length=max_message_length, 
                         client_manager=client_manager, 
                         topic_name=topic_name)
    server.start()
    return server

class KafkaServer(StoppableThread):
    def __init__(self, *args, **kwargs) -> None:
        super(KafkaServer, self).__init__(name="KafkaServer")
        self.server_address = kwargs["server_address"]
        self.client_manager : SimpleClientManager = kwargs["client_manager"]
        self.topic_name = kwargs["topic_name"]
        self.max_message_length = kwargs["max_message_length"]
        self.registered_cids = dict()
        self.clientmsg_deserializer=flwr_dot_proto_dot_transport__pb2.ClientMessage.FromString,
        self.serverresponse_serializer=flwr_dot_proto_dot_transport__pb2.ServerMessage.SerializeToString,

        pass
    def stopServer(self, grace=1):
        time.sleep(grace)
        self.server_msg_sender.close()
        self.serverReceiver.stop()
        self.stopThreads()
        self.thread.stop()
    def run(self):
        try:
            while not self.stopped():
                self.__startServerReceiver()
                self.__initServerMsgSender()
                self._stop_event.wait()
                log(INFO, "Stopping Flower Kafka server")
                self.stopServer(grace=0)
        except:
            print("Client connection stopped")
    
    def __startServerReceiver(self):
        self.serverReceiver = MsgReceiver(self.server_address,
                             options={
                                "max_send_message_length": self.max_message_length,
                                "max_receive_message_length": self.max_message_length,
                                "topic_name": self.topic_name,
                                "log" : log,
                                "auto_offset_reset" : "latest",
                                "cid" : "FLserverReceiver"
                             },
        )
        self.servicer = fss.FlowerServiceServicer(self.client_manager)
        self.serverReceiver.start()
        self.thread = StoppableThread(name="ServerReceiverMsgThread", target = self.receiveMsgs, args = ())
        self.thread.start()
    
    def __initServerMsgSender(self):
        self.server_msg_sender = MsgSender(
            self.server_address,
            options={
                "max_send_message_length": self.max_message_length,
                "max_receive_message_length": self.max_message_length,
                "log" : log
            },
        )

    def stopThreads(self):
        for t in self.registered_cids:
            log(DEBUG, f"Stopping sender thread for {t}")
            self.registered_cids[t].stop()
        self.registered_cids = {} #not the best delete TODO
    def stopClientThread(self, cid):
        log(DEBUG, f"Stopping sender thread for {cid}")
        t : KafkaServer.senderThread = self.registered_cids.pop(cid, None)
        if t is not None:
            t.stop()
        else:
            log(INFO, f"Sender thread not found for {cid}")
    def receiveMsgs(self):
        log(INFO, "Starting server receiver thread")
        try:
            while(not self.stopped()):
                msg = self.serverReceiver.getNextMsg(block=True, timeout=1000)
                if self.stopped():
                    log(INFO,"Kafka server interrupted")
                    break
                if msg is None:
                    continue
                log(INFO,"Got new message in server receiver")

                #need to deserialize msg, get cid and push the msg to bridge
                cid, clientmsg = self.getClientMessage(msg)
                cid :str = cid
                thread = None
                if cid in self.registered_cids: #find running sender thread if exists and push to it
                    thread : KafkaServer.senderThread = self.registered_cids[cid]
                    if thread.stopped() or clientmsg is None: #if client is registering again. reset the pipeline
                        log(INFO, f'Client server sender thread not running {clientmsg}')
                        self.client_manager.unregistercid(cid)
                        thread.stop()
                        thread = None

                if thread is None:
                    thread : KafkaServer.senderThread = self.servermsgSender(cid)
                    self.registered_cids[cid] = thread
                    thread.start()
                if clientmsg is not None:
                    log(INFO, f"Pushing new msg to cid {cid}")
                    thread.add(clientmsg)
                    log(DEBUG, f"Done pushing msg to cid {cid}")
                else:
                    log(INFO, f"Received registration for cid {cid}")
        except:
            log(DEBUG, "Error: client connection!", sys.exc_info()[1])
        finally:
            log(INFO, "Stopping server receiver thread")
    
    def inputmsg(self, q):
        for msg in iter(q.get, None):
            yield msg
    
    @staticmethod
    class senderThread(StoppableThread):
        def __init__(self, **kwargs: Mapping[str, Any]) -> None:
            super(KafkaServer.senderThread, self).__init__(name=kwargs["name"],
                            kwargs=kwargs)
            self.cid : str = kwargs["cid"]
            self.q : Queue = Queue()
            self.caller : KafkaServer = kwargs["server"]
            self.daemon = True
        
        def add(self, msg : ClientMessage):
            self.q.put(msg)
            
        def run(self) -> None:
            inputiterator = self.caller.inputmsg(self.q)
            servermsgIterator = self.caller.servicer.Join(inputiterator, self.cid)
            #returns iterator with next msg from server to client
            while not self.stopped() and not self.caller.stopped():
                try:
                    msg : ServerMessage = next(servermsgIterator)
                    log(DEBUG, f"Got new msg from server for {self.cid}")
                    msgdata = self.caller.getServerMessageBinary(self.cid, msg)
                    self.caller.server_msg_sender.sendMsg(msgdata, f"FLclient{self.cid}")
                    log(DEBUG, f"Msg for cid {self.cid} sent")
                except:
                    break
            log(INFO, f"Stopped server sender thread for {self.cid}")

    def servermsgSender(self, cid):
        log(INFO, f"Starting server sender thread for {cid}")
        
        thread = KafkaServer.senderThread(cid=cid,name=f'sender-thread-{cid}',
                              server=self)
        return thread


    def getServerMessageBinary(self, cid : str, servermsg : ServerMessage):
        payloadstr = servermsg.SerializeToString()
        payload = {"cid" : cid, "payload" : str(payloadstr.hex())}
        return str(payload).encode('utf-8')
    def getClientMessage(self, msgdata) -> tuple([str, ClientMessage]):
        strdata = msgdata.decode("utf-8")
        strdata = strdata.replace('\'','"')
        jdata = json.loads(strdata)
        cid = jdata["cid"]
        if len(jdata['payload']) == 0:
            clientmsg = None
        else:
            clientmsg = ClientMessage.FromString(bytes.fromhex(jdata['payload']))
        return cid, clientmsg
    