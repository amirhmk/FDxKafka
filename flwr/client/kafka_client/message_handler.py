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
        log(DEBUG, "Kafka get parameters msg")
    elif server_msg.HasField("fit_ins"):
        log(DEBUG, "Kafka handle fit msg")
    elif server_msg.HasField("evaluate_ins"):
        log(DEBUG, "Kafka handle evaluate msg")
    elif server_msg.HasField("properties_ins"):
        log(DEBUG, "Kafka handle properties msg")
    else:
        log(DEBUG, "Kafka handle Unknown msg")


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



# def _get_parameters(client: Client) -> KafkaClientMessage:
#     # No need to deserialize get_parameters_msg (it's empty)
#     parameters_res = client.get_parameters()
#     # parameters_res_proto = serde.parameters_res_to_proto(parameters_res)
#     # return parameters_res
#     payload = { "parameters": parameters_res.parameters.tensors }
#     return KafkaClientMessage(type="parameters_res", payload={})


# def _get_properties(
#     client: Client, properties_msg
# ) -> KafkaMessage:
#     # Deserialize get_properties instruction
#     properties_ins = parse_get_properties_ins(properties_msg)
#     # Request for properties
#     properties_res = client.get_properties(properties_msg)
#     # Serialize response
#     payload = { "properties": properties_res }
#     return KafkaClientMessage(type="properties_res", payload={})


# def _fit(client: Client, fit_msg) -> KafkaMessage:
#     # Deserialize fit instruction
#     server_address, fit_ins = parser.fit_ins_from_kafka(fit_msg)
#     sendMsg = start_train(server_address, fit_ins)
#     # Perform fit
#     fit_res = client.fit(fit_ins)
#     # Serialize fit result
#     fit_res_kafka = parser.fit_res_to_kafka(fit_res)
#     return sendMsg, KafkaClientMessage(type="fit_res", payload=fit_res_kafka)


# def _evaluate(client: Client, evaluate_msg) -> KafkaMessage:
#     # Deserialize evaluate instruction
#     # evaluate_ins = serde.evaluate_ins_from_proto(evaluate_msg)
#     evaluate_ins = parser.parse_evaluate_ins(evaluate_msg)
#     # Perform evaluation
#     evaluate_res = client.evaluate(evaluate_ins)
#     # Serialize evaluate result
#     payload = { "properties": evaluate_res }
#     return KafkaClientMessage(type="evaluate_res", payload={})


# def _reconnect(
#     reconnect_msg,
# ) -> Tuple[KafkaMessage, int]:
#     # Determine the reason for sending Disconnect message
#     reason = Reason.ACK
#     sleep_duration = None
#     if reconnect_msg.seconds is not None:
#         reason = Reason.RECONNECT
#         sleep_duration = reconnect_msg.seconds
#     # Build Disconnect message
#     disconnect = ClientMessage.Disconnect(reason=reason)
#     return ClientMessage(disconnect=disconnect), sleep_duration

# def start_train(server_address, train_ins):
#     # start producer in a new thread
#     producer_channel = MsgSender(
#         server_address,
#         options=train_ins.config,
#     )
#     log(DEBUG, f"Started Kafka Producer to topic={train_ins.config['topic_name']}")
#     return producer_channel.sendMsg

