"""
Common types related to all transports
"""
from abc import ABC, abstractmethod
from enum import Enum


class TransportMessageType(Enum):
    RPC_REQ = 1
    RPC_RESP = 2


class AbstractTransport(ABC):

    @abstractmethod
    def send(self, message_type, msg_id, remote_endpoint, message, serializer, timeout_spec):
        pass  # fixme: TBD implement this

    @abstractmethod
    def receive(self, msg_id, remote_endpoint, timeout_spec):
        pass  # fixme: TBD implement this

    @abstractmethod
    def block_until_completed(self, msg_id, timeout_spec):
        pass  # fixme: TBD implement this

    @abstractmethod
    def cancel(self, msg_id):
        pass  # fixme: TBD implement this
