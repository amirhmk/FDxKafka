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
"""Flower server app."""

import sys
from logging import INFO
from typing import Dict, Optional, Tuple
from flwr.common import GRPC_MAX_MESSAGE_LENGTH
from flwr.common import KAFKA_MAX_MESSAGE_LENGTH
from flwr.common.logger import log
from flwr.server.client_manager import SimpleClientManager #, KafkaClientManager
from flwr.server.kafka_server.kafka_server import start_kafka_receiver
from flwr.server.grpc_server.grpc_server import start_insecure_grpc_server
from flwr.server.server import Server
from flwr.server.strategy import FedAvg, Strategy
from flwr.server.kafka_server.kafka_server import KafkaServer

DEFAULT_USE_KAFKA = True
SERVER_TOPIC = "FLserver"

GRPC_DEFAULT_SERVER_ADDRESS = "[::]:8080"
GRPC_MAX_MESSAGE_LENGTH = GRPC_MAX_MESSAGE_LENGTH

KAFKA_DEFAULT_SERVER_ADDRESS = "localhost:9092"
KAFKA_MAX_MESSAGE_LENGTH = KAFKA_MAX_MESSAGE_LENGTH


def start_server(  # pylint: disable=too-many-arguments
    use_kafka : bool,
    server_address: str = GRPC_DEFAULT_SERVER_ADDRESS,
    server: Optional[Server] = None,
    config: Optional[Dict[str, int]] = None,
    strategy: Optional[Strategy] = None,
    max_message_length: int = GRPC_MAX_MESSAGE_LENGTH,
    force_final_distributed_eval: bool = False,
    
) -> None:
    """Start a Flower server using the Kafka transport layer.

    Arguments:
        server_address: Optional[str] (default: `"[::]:8080"`). The IPv6
            address of the server.
        server: Optional[flwr.server.Server] (default: None). An implementation
            of the abstract base class `flwr.server.Server`. If no instance is
            provided, then `start_server` will create one.
        config: Optional[Dict[str, int]] (default: None). The only currently
            supported values is `num_rounds`, so a full configuration object
            instructing the server to perform three rounds of federated
            learning looks like the following: `{"num_rounds": 3}`.
        strategy: Optional[flwr.server.Strategy] (default: None). An
            implementation of the abstract base class `flwr.server.Strategy`.
            If no strategy is provided, then `start_server` will use
            `flwr.server.strategy.FedAvg`.
        grpc_max_message_length: int (default: 536_870_912, this equals 512MB).
            The maximum length of gRPC messages that can be exchanged with the
            Flower clients. The default should be sufficient for most models.
            Users who train very large models might need to increase this
            value. Note that the Flower clients need to be started with the
            same value (see `flwr.client.start_client`), otherwise clients will
            not know about the increased limit and block larger messages.
        force_final_distributed_eval: bool (default: False).
            Forces a distributed evaulation to occur after the last training
            epoch when enabled.

    Returns:
        None.
    """
    initialized_server, initialized_config = _init_defaults(server, config, strategy)

    print("use kafka", use_kafka, server_address)
    if use_kafka:
        # Start server
        max_message_length = KAFKA_MAX_MESSAGE_LENGTH
        kafka_server : KafkaServer = start_kafka_receiver(client_manager=initialized_server.client_manager(),
            server_address=server_address,
            max_message_length=max_message_length,
            topic_name = SERVER_TOPIC)
        initialized_server.kafka_receiver = kafka_server
    else:
        # Start gRPC server
        grpc_server = start_insecure_grpc_server(
            client_manager=initialized_server.client_manager(),
            server_address=server_address,
            max_message_length=max_message_length,
        )
    log(
        INFO,
        "Kafka server running (insecure, %s rounds)",
        initialized_config["num_rounds"],
    )
    kafka_server.address = server_address
    _fl(
        server=initialized_server,
        config=initialized_config,
        force_final_distributed_eval=force_final_distributed_eval,
    )

    if use_kafka:
        # Stop the kafka server
        kafka_server.stop()
        sys.exit(0)
    else:
        # Stop the gRPC server
        grpc_server.stop(grace=1)


def _init_defaults(
    server: Optional[Server],
    config: Optional[Dict[str, int]],
    strategy: Optional[Strategy],
) -> Tuple[Server, Dict[str, int]]:
    # Create server instance if none was given
    if server is None:
        # if not USE_KAFKA:
        client_manager = SimpleClientManager()
        # else:
        #     client_manager = KafkaClientManager()
        if strategy is None:
            strategy = FedAvg(min_fit_clients=config['min_fit_clients'],
                              min_eval_clients=1,
                              min_available_clients=1)
        server = Server(client_manager=client_manager, strategy=strategy)

    # Set default config values
    if config is None:
        config = {}
    if "num_rounds" not in config:
        config["num_rounds"] = 1

    return server, config


def _fl(
    server: Server, config: Dict[str, int], force_final_distributed_eval: bool
) -> None:
    # Fit model
    hist = server.fit(num_rounds=config["num_rounds"])
    log(INFO, "app_fit: losses_distributed %s", str(hist.losses_distributed))
    log(INFO, "app_fit: metrics_distributed %s", str(hist.metrics_distributed))
    log(INFO, "app_fit: losses_centralized %s", str(hist.losses_centralized))
    log(INFO, "app_fit: metrics_centralized %s", str(hist.metrics_centralized))

    if force_final_distributed_eval:
        # Temporary workaround to force distributed evaluation
        server.strategy.eval_fn = None  # type: ignore

        # Evaluate the final trained model
        res = server.evaluate_round(rnd=-1)
        if res is not None:
            loss, _, (results, failures) = res
            log(INFO, "app_evaluate: federated loss: %s", str(loss))
            log(
                INFO,
                "app_evaluate: results %s",
                str([(res[0].cid, res[1]) for res in results]),
            )
            log(INFO, "app_evaluate: failures %s", str(failures))
        else:
            log(INFO, "app_evaluate: no evaluation result")

    # Graceful shutdown
    server.disconnect_all_clients()


if __name__ == '__main__':
    import flwr as fl
    import argparse
    a = argparse.ArgumentParser()
    a.add_argument("--broker", help="kafka broker")
    args = a.parse_args()
    print(args)
    

    # server = server_address
    fl.server.start_server(server_address=args.broker, config={"num_rounds": 3})