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
"""Flower ClientManager."""

import sys
import random
import threading
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from logging import INFO,DEBUG
from flwr.common.logger import log
from .client_proxy import ClientProxy
from .criterion import Criterion


class ClientManager(ABC):
    """Abstract base class for managing Flower clients."""

    @abstractmethod
    def num_available(self) -> int:
        """Return the number of available clients."""

    @abstractmethod
    def register(self, client: ClientProxy) -> bool:
        """Register Flower ClientProxy instance.

        Returns:
            bool: Indicating if registration was successful
        """

    @abstractmethod
    def unregister(self, client: ClientProxy) -> None:
        """Unregister Flower ClientProxy instance."""

    @abstractmethod
    def all(self) -> Dict[str, ClientProxy]:
        """Return all available clients."""

    @abstractmethod
    def wait_for(self, num_clients: int, timeout: int) -> bool:
        """Wait until at least `num_clients` are available."""

    @abstractmethod
    def sample(
        self,
        num_clients: int,
        min_num_clients: Optional[int] = None,
        criterion: Optional[Criterion] = None,
    ) -> List[ClientProxy]:
        """Sample a number of Flower ClientProxy instances."""


class SimpleClientManager(ClientManager):
    """Provides a pool of available clients."""

    def __init__(self) -> None:
        self.clients: Dict[str, ClientProxy] = {}
        self._cv = threading.Condition()
        self.threadLock = threading.Lock()
    def __len__(self) -> int:
        try:
            self.threadLock.acquire()
            return len(self.clients)
        finally:
            self.threadLock.release()

    def wait_for(self, num_clients: int, timeout: int = 86400) -> bool:
        """Block until at least `num_clients` are available or until a timeout
        is reached.

        Current timeout default: 1 day.
        """
        log(DEBUG, f"Going to wait for {num_clients}")
        with self._cv:
            try:
                return self._cv.wait_for(
                    lambda: len(self) >= num_clients, timeout=timeout
                )
            except:
                log(DEBUG, "Error: client connection!", sys.exc_info()[1])
            finally:
                log(DEBUG, f"Finally left after waiting for {num_clients} \
                            clients having {len(self)} clients")


    def num_available(self) -> int:
        """Return the number of available clients."""
        return len(self)

    def register(self, client: ClientProxy) -> bool:
        """Register Flower ClientProxy instance.

        Returns:
            bool: Indicating if registration was successful. False if ClientProxy is
                already registered or can not be registered for any reason
        """
        log(INFO, f"Registering cid {client.cid} in CM")
        if client.cid in self.clients:
            return False
        log(DEBUG, f"Goint to add client {client.cid} with {len(self.clients)}")
        try:
            self.threadLock.acquire()
            self.clients[client.cid] = client
        finally:
            self.threadLock.release()
        with self._cv:
            self._cv.notify_all()
        log(INFO, f"Number of clients after registration: {len(self.clients)}")
        return True
    
    def unregistercid(self, cid : str) -> None:
        if cid in self.clients:
            log(DEBUG, f"Goint to remove client {cid}  from CM with {len(self.clients)}")
            self.unregister(self.clients[cid])
            log(INFO, f"{len(self.clients)} clients left")

    def unregister(self, client: ClientProxy) -> None:
        """Unregister Flower ClientProxy instance.

        This method is idempotent.
        """
        if client.cid in self.clients:
            try:
                self.threadLock.acquire()
                del self.clients[client.cid]
            except:
                self.threadLock.release()
            client.bridge.close()
            with self._cv:
                self._cv.notify_all()

    def all(self) -> Dict[str, ClientProxy]:
        """Return all available clients."""
        return self.clients

    def sample(
        self,
        num_clients: int,
        min_num_clients: Optional[int] = None,
        criterion: Optional[Criterion] = None,
    ) -> List[ClientProxy]:
        """Sample a number of Flower ClientProxy instances."""
        # Block until at least num_clients are connected.
        if min_num_clients is None:
            min_num_clients = num_clients
        self.wait_for(min_num_clients)
        # Sample clients which meet the criterion
        available_cids = list(self.clients)
        if criterion is not None:
            available_cids = [
                cid for cid in available_cids if criterion.select(self.clients[cid])
            ]
        sampled_cids = random.sample(available_cids, num_clients)
        return [self.clients[cid] for cid in sampled_cids]


# class KafkaClientManager(SimpleClientManager):
#     def __init__(self) -> None:
#         super(KafkaClientManager, self).__init__()
    
#     def register(self, client: ClientProxy) -> bool:
#         return super().register(client)
#     def unregister(self, client: ClientProxy) -> None:
#         return super().unregister(client)