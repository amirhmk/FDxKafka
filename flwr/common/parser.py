"""Kafka Message Serilization and deserialization"""

from flwr.common.parameter import ndarray_to_bytes, weights_to_parameters
from flwr.common.typing import KafkaMessage
from . import typing
import numpy as np

def metrics_from_kafka():
    """Deserialize... ."""
    # metrics = {}
    # for k in proto:
    #     metrics``
    # pass

def metrics_to_kafka():
    """This should alreaady be done by json parser"""
    pass

def parameters_from_kafka(parameters):
    """Deserialize kafka into Parameters"""
    tensors: List[bytes] = np.asarray(parameters["tensors"])
    return weights_to_parameters(tensors)


def parameters_to_kafka(parameters: typing.Parameters):
    """Serialize parameters for Kafka"""
    pass


def parameters_res_to_kafka(res: typing.ParametersRes) -> KafkaMessage:
    """."""
    parameters_proto = parameters_to_kafka(res.parameters)
    return parameters_proto

def fit_ins_to_kafka(ins: typing.FitIns) -> KafkaMessage:
    """Serialize flower.FitIns to Kafka message."""
    parameters_proto = parameters_to_kafka(ins.parameters)
    config_msg = metrics_to_kafka(ins.config)
    return KafkaMessage(parameters=parameters_proto, config=config_msg)

def fit_ins_from_kafka(msg) -> typing.FitIns:
    """Deserialize flower.FitIns from Kafka message."""
    server_address = msg['server_address']
    config = {"max_send_message_length": msg['max_send_message_length'],
            "max_receive_message_length": msg['max_receive_message_length'],
            "topic_name": msg['topic_name']}

    parameters = parameters_from_kafka(msg['parameters'])
    del msg['parameters']
    config = msg
    return server_address, typing.FitIns(parameters=parameters, config=config)

def fit_res_to_kafka(res: typing.FitRes) -> KafkaMessage:
    """Serialize flower.FitIns to Kafka message."""
    parameters = parameters_to_kafka(res.parameters)
    metrics_msg = None if res.metrics is None else metrics_to_kafka(res.metrics)

    return KafkaMessage(
        parameters=parameters,
        num_examples=res.num_examples,
        metrics=metrics_msg,
    )

def fit_res_from_kafka(msg: KafkaMessage) -> typing.FitRes:
    """Deserialize flower.FitRes from Kafka message."""
    parameters = parameters_from_kafka(msg.parameters)
    metrics = None if msg.metrics is None else metrics_from_kafka(msg.metrics)
    return typing.FitRes(
        parameters=parameters,
        num_examples=msg.num_examples,
        metrics=metrics,
    )


def evaluate_ins_from_kafka(msg):
    """Deserialize flower.EvaluateIns from Kafka message."""
    pass

def evaluate_res_to_kafka(res):
    """Serialize flower.EvaluateIns to Kafka message."""
    pass

def evaluate_res_from_kafka(msg) -> typing.EvaluateRes:
    """Deserialize flower.EvaluateRes from Kafka message."""
    