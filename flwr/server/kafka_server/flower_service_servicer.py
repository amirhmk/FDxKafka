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
"""Servicer for FlowerService.

Relevant knowledge for reading this modules code:
    - https://github.com/grpc/grpc/blob/master/doc/statuscodes.md
"""
import sys
from logging import INFO,DEBUG
from flwr.common.logger import log
from typing import Callable, Iterator
from flwr.proto.transport_pb2 import ClientMessage, ServerMessage
from flwr.server.client_manager import ClientManager
from flwr.server.kafka_server.kafka_bridge import KafkaBridge
from flwr.server.kafka_server.kafka_client_proxy import KafkaClientProxy


def default_bridge_factory() -> KafkaBridge:
    """Return KafkaBridge instance."""
    return KafkaBridge()

def default_kafka_client_factory(cid: str, bridge: KafkaBridge) -> KafkaClientProxy:
    """Return GrpcClientProxy instance."""
    return KafkaClientProxy(cid=cid, bridge=bridge)


def register_client(
    client_manager: ClientManager,
    client: KafkaClientProxy,
    cid : str,
    # context: grpc.ServicerContext,
) -> bool:
    """Try registering GrpcClientProxy with ClientManager."""
    is_success = client_manager.register(client)

    # if is_success:

        # def rpc_termination_callback() -> None:
        #     client.bridge.close()
        #     client_manager.unregister(client)

        # context.add_callback(rpc_termination_callback) #add shutdown hooks TODO
    return is_success


class FlowerServiceServicer():#transport_pb2_grpc.FlowerServiceServicer
    """FlowerServiceServicer for bi-directional gRPC message stream."""

    def __init__(
        self,
        client_manager: ClientManager,
        kafka_bridge_factory: Callable[[], KafkaBridge] = default_bridge_factory,
        kafka_client_factory: Callable[
            [str, KafkaBridge], KafkaClientProxy
        ] = default_kafka_client_factory,
    ) -> None:
        self.client_manager: ClientManager = client_manager
        self.kafka_bridge_factory = kafka_bridge_factory
        self.client_factory = kafka_client_factory


    #called when service joins channel
    def Join(  # pylint: disable=invalid-name
        self,
        request_iterator: Iterator[ClientMessage],
        cid : str
        # context: grpc.ServicerContext,
    ) -> Iterator[ServerMessage]: # inverse order. client initiates comm
        """Method will be invoked by each GrpcClientProxy which participates in
        the network.

        Protocol:
            - The first message is sent from the server to the client ---------> we'll change it other way around. client will register with server
            - Both ServerMessage and ClientMessage are message "wrappers"
                wrapping the actual message
            - The Join method is (pretty much) protocol unaware
        """
        log(INFO, f"Joined cid {cid}")
        bridge = self.kafka_bridge_factory()
        client = self.client_factory(cid, bridge)
        log(DEBUG, f"Registering cid {cid}")
        is_success = register_client(self.client_manager, client, cid)
        log(DEBUG, f"Register cid {cid} is {is_success}")
        #send client registration success? TODO
        
        if is_success:
            # Get iterators
            client_message_iterator = request_iterator #push client message in here
            server_message_iterator = bridge.server_message_iterator()

            # All messages will be pushed to client bridge directly
            while True:
                try:
                    # Get server message from bridge and yield it
                    #push to client topic
                    log(DEBUG, f"Getting new server msg for {cid}")
                    server_message = next(server_message_iterator)
                    yield server_message
                    # Wait for client message from topic
                    client_message = next(client_message_iterator)
                    bridge.set_client_message(client_message)
                except StopIteration:
                    break
                except:
                    print(sys.exc_info())
                    print("Oops!", sys.exc_info()[1], "occurred.")
