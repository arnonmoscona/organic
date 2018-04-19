from unittest import TestCase
from unittest.mock import Mock

from free_range.core.client.tests.papi.rpc_test_papi_pb2 import (RpcRequestA,
                                                                 RpcResponseA)
from free_range.core.common.time import TickTimeSource, TimeoutSpecification
from free_range.transport.local.local_transport import LocalTransport
from free_range.transport.types import TransportMessageType


def mock_wrap(message_type, msg_id, endpoint_location, message, serializer, timeout_spec,
              expect_response, response_to=None):
    return (message_type, msg_id, endpoint_location, message, serializer,
            timeout_spec, expect_response, response_to)


def mock_unwrap(wrapped):
    (message_type, msg_id, endpoint_location, message, serializer, timeout_spec, expect_response,
     response_to) = wrapped
    return message


def mock_message_matches(wrapped_message, endpoint_location, request_id):
    (message_type, msg_id, endpoint_location, message, serializer, timeout_spec,
     expect_response, response_to) = wrapped_message
    return request_id == msg_id


def mock_execute(wrapped_message):
    (message_type, msg_id, endpoint_location, message, serializer, timeout_spec,
     expect_response, response_to) = wrapped_message
    return(mock_wrap(message_type, 1000 + msg_id, endpoint_location, message, serializer,
                     timeout_spec, expect_response, response_to=msg_id))


def mock_response_matches(wrapped_message, endpoint_location, request_id):
    (message_type, msg_id, endpoint_location, message, serializer, timeout_spec,
     expect_response, response_to) = wrapped_message
    return response_to == request_id


class LocalTransportTestMixin(TestCase):
    def setUp(self):
        self.calls = []

        def echo(msg):
            self.calls.append(msg)
            return RpcResponseA(f'echo {msg.request}')

        self.resolver = Mock()
        self.control_layer = Mock()
        self.control_layer.wrap = mock_wrap
        self.control_layer.unwrap_response = mock_unwrap
        self.control_layer.message_matches = mock_message_matches
        self.control_layer.is_expired.return_value = False
        self.control_layer.execute = self.execute
        self.control_layer.response_matches = mock_response_matches

        self.time_source = TickTimeSource()
        self.transport = LocalTransport(self.resolver, self.control_layer, self.time_source)
        self.request = RpcRequestA(request='hi')
        self.endpoint_location = Mock()
        self.endpoint_location.callable.return_value = echo
        self.serializer = Mock()
        self.timeout_spec = TimeoutSpecification(10, self.time_source.units)

    def execute(self, wrapped_message):
        (message_type, msg_id, endpoint_location, message, serializer,
         timeout_spec, expect_response,
         response_to) = wrapped_message
        self.calls.append(message.request)
        return mock_execute(wrapped_message)


class SendTests(LocalTransportTestMixin):
    def test_send_does_not_blow_up_on_request_with_response_requested(self):
        self.transport.send(TransportMessageType.RPC_REQ, 1, self.endpoint_location, self.request,
                            self.serializer, self.timeout_spec, expect_response=True)

    def test_send_does_not_blow_up_on_request_with_response_not_requested(self):
        self.transport.send(TransportMessageType.RPC_REQ, 1, self.endpoint_location,
                            self.request, self.serializer, self.timeout_spec,
                            expect_response=False)

    def test_send_is_eager_if_response_is_expected(self):
        self.transport.send(TransportMessageType.RPC_REQ, 1, self.endpoint_location, self.request,
                            self.serializer, self.timeout_spec, expect_response=True)
        self.assertEqual(['hi'], self.calls)

    def test_send_is_eager_if_response_is_not_requested(self):

        self.transport.send(TransportMessageType.RPC_REQ, 1, self.endpoint_location, self.request,
                            self.serializer, self.timeout_spec, expect_response=False)
        self.assertEqual(['hi'], self.calls)

    def test_when_executing_requests_they_are_fifo(self):
        request2 = RpcRequestA(request='hi too')
        request3 = RpcRequestA(request='hi tree')
        for r in [self.request, request2, request3]:
            self.transport.send(TransportMessageType.RPC_REQ, 1, self.endpoint_location,
                                r, self.serializer, self.timeout_spec, expect_response=False)
        self.assertEqual(['hi', 'hi too', 'hi tree'], self.calls)

# fixme: validate sequences of control layer invocation methods by transport
