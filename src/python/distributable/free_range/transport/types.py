"""
Common types related to all transports
"""
from abc import ABC, abstractmethod
from enum import Enum

from free_range.core.common.decorators import public_interface


class TransportMessageType(Enum):
    """
    An enumeration of fine grain message types. Each interaction patterns has
    one or more message types depending on the role of the message in the pattern.
    For instance, the message can be a request or a response. It may be a control
    message of some kind. The message type is important in some transports as
    well as in the framework beavior with respect to some of the transport layer facilities,
    like full state transfer, security plugins etc.
    """
    RPC_REQ = 1
    RPC_RESP = 2


class AbstractTransport(ABC):
    """
    The base class to all transports. The transport is responsible for the concrete
    implementation of transmitting messages among endpoints. A transport may support one or more
    messaging patterns. Transports are statefulk and manage buffers and other constructs to track
    whatever state is needed to support the API, for instance tracking outstanding requests,
    managing backpressure, and negotiating connections..

    The primary purposes of the transport is to simplify the client API and encapsulate the
    complexitty of the distributes communications.

    Transports are universal and present a low level API that consists only of send, receive,
    and cancel operations. While they support multiple patterns, it is the responsibility of a
    higher level class to present a pattern-appropriate API.
    """

    @abstractmethod
    @public_interface
    def send(self, message_type, msg_id, endpoint_location, message, serializer, timeout_spec,
             expect_response=False):
        """
        Does the actual dispatching of a message over a concrete transport.
        This is a blocking call. It is blocking in order to prevent piling the up of requests on
        the client side.
        :param message_type: the fine grain message type. One of TransportMessageType.
        :param msg_id: The unique ID of the message
        :param endpoint_location: A fully resolved endpoint location that is appropriate for the
            specific message type. Created by a message router.
        :param message: the message itself
        :param serializer: the serializer for the message
        :param timeout_spec: a required timeout specification for the message. All types have a
            timeout, which at the very least expresses a send timeout. It can also act as a
            response timeout for request message types that expect a response.
        :param expect_response: tells the transport whether or not to expect a response for the
            message. If True, then the transport would normally need to store some state for
            tracking. If True, then the timeout specification also implies that the state may
            be discarded after timeout expired and that any response that is received after
            the thimeout expiration may be silently dropped.
        :return: None
        """
        # fixme: document exceptions
        raise NotImplementedError('This is an abstract method. Must be implemented in subclasses')

    @abstractmethod
    @public_interface
    def receive(self, endpoint_location, timeout_spec, response_to=None):
        """
        The counterpart of send. A non-blocking call that asks the framework for a message from a
        remote party. In some contexts, such as an RPC client, the receiver is expecting a
        message that is associated with a specific past message, usually a response.
        :param endpoint_location: the fully resolved endpoint
        :param timeout_spec: receive timeout specification
        :param response_to: an optional (may be None) "request" message ID. When set this instructs
            the framework to filter for messages that specify that they are a response to this ID.
        :return:
        """
        raise NotImplementedError('This is an abstract method. Must be implemented in subclasses')

    @abstractmethod
    @public_interface
    def cancel(self, msg_id):
        """
        Canlcles any activity related to msg_id as soon as feasible. This will cancel a pending
        send if it can and will also cancel any waiting for a response to this message if such
        state exists.
        This method provides no guarantee that all network activity related to the message is
        canceled, nor will it abort any remote processing of the message. Depending on the
        message pattern in use, response to the message may still be received.
        :param msg_id: the message to cancel
        """
        raise NotImplementedError('This is an abstract method. Must be implemented in subclasses')

    # fixme: define the future that receive returns. Allows receive to be the remote RPC service
