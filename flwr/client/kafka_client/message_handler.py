import json
from typing import Tuple
from flwr.client.kafka_client.connection import getCid
from flwr.proto import transport_pb2 as flwr_dot_proto_dot_transport__pb2
from flwr.proto.transport_pb2 import ClientMessage, Reason, ServerMessage
from flwr.client.client import Client
from flwr.common import KafkaMessage
from kafka_producer.producer import MsgSender
from logging import INFO, DEBUG
from flwr.common.logger import log
from flwr.common import parser
from flwr.common.parameter import parameters_to_weights
from flwr.client.grpc_client.message_handler import handle


def getServerMessage(msgdata) -> tuple([str, ServerMessage]):
    strdata = msgdata.decode("utf-8")
    strdata = strdata.replace('\'','"')
    jdata = json.loads(strdata)
    cid = jdata["cid"]
    servermsg = ServerMessage.FromString(bytes.fromhex(jdata['payload']))
    return cid, servermsg
def getClientMessageBinary(cid : str, clientmsg : ClientMessage):
    payloadstr = clientmsg.SerializeToString()
    payload = {"cid" : cid, "payload" : payloadstr.hex()}
    return str(payload).encode('utf-8')

def KafkaClientMessage(cid: str, payload: dict) -> KafkaMessage:
    return {
        "cid": cid,
        "payload": payload
    }


class UnknownServerMessage(Exception):
    """Signifies that the received message is unknown."""

def logtype(server_msg : ServerMessage) -> None:
    if server_msg.HasField("reconnect"):
        log(DEBUG, "Kafka handle reconnect msg")
    elif server_msg.HasField("get_parameters"):
        log(DEBUG, "Kafka get_parameters() msg")
    elif server_msg.HasField("fit_ins"):
        log(DEBUG, "Kafka handle fit() msg")
    elif server_msg.HasField("evaluate_ins"):
        log(DEBUG, "Kafka handle evaluate() msg")
    elif server_msg.HasField("properties_ins"):
        log(DEBUG, "Kafka handle properties() msg")
    else:
        log(DEBUG, "Kafka handle Unknown msg type")


def handle_kafka(
    client: Client, server_msg : ServerMessage, cid : str
) -> Tuple[KafkaMessage, int, bool]:
    msgcid, servermsg = getServerMessage(server_msg)
    logtype(servermsg)
    if cid != msgcid:
        log(INFO, f"Msg cid not the same! Received:{cid} and msg cid {msgcid}")
    clientmsg, ret1, ret2 = handle(client, servermsg)
    log(DEBUG, "Sending reply msg")
    msg : ClientMessage = clientmsg
    newmsg = getClientMessageBinary(cid, msg)
    return newmsg, ret1, ret2
