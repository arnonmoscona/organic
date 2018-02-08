from unittest import TestCase
from unittest.mock import Mock
from uuid import UUID

from free_range.core.client.base_client import BaseClient
from free_range.core.client.tests.papi.rpc_test_papi_pb2 import (RpcRequestA,
                                                                 RpcResponseA)
from free_range.core.common.endpoints import RpcEndpoint
from free_range.core.common.exceptions import InvalidArgumentError
from free_range.core.common.serializers import RpcProtobufSerializer
from free_range.core.common.tests.random_mixin import RandomMixin
from free_range.core.common.time import TickTimeSource


class BaseClientTestMixin(TestCase):
    def setUp(self):
        self.transport = Mock()
        self.time_source = TickTimeSource().auto_advance(True)
        self.client = BaseClient(self.transport, default_timeout=10, time_source=self.time_source)


class BaseClientConstructorTests(BaseClientTestMixin):
    def test_client_indicates_the_transport_passed_to_the_constructor(self):
        self.assertEqual(self.transport, self.client.transport)

    def test_client_rejects_none_as_transport(self):
        with self.assertRaises(InvalidArgumentError):
            BaseClient(None, default_timeout=10)


class GenerateCallIdTests(BaseClientTestMixin):
    def test_generate_call_id_returns_different_values_each_time_for_same_endpoint(self):
        id1 = self.client.generate_call_id()
        id2 = self.client.generate_call_id()
        self.assertNotEqual(id1, id2, 'call IDs must not be constant')

    def test_the_base_id_generated_is_a_uuid(self):
        self.assertEqual(UUID, type(self.client.generate_call_id()))


class GetTimestampTests(RandomMixin, BaseClientTestMixin):
    def test_if_a_time_source_is_provided_then_it_is_used_for_the_timestamp(self):
        source = TickTimeSource()
        t = self.random_natural()
        source.advance(t)
        client = BaseClient(self.transport, default_timeout=10, time_source=source)
        t2 = client.get_timestamp()
        self.assertEqual(t, t2, 'expected to get the time sources timestamp')


class WithEndpointTestMixin(BaseClientTestMixin):
    def setUp(self):
        super().setUp()
        pkg = 'free_range.core.client.tests.papi.rpc_test_papi_pb2'
        self.req_type = f'{pkg}.RpcRequestA'
        self.response_type = f'{pkg}.RpcResponseA'
        self.endpoint_json = ('{"callable": "func.ref", '
                              f'"argumentType": "{self.req_type}", '
                              f'"returnType": "{self.response_type}"'
                              '}')
        self.endpoint = RpcEndpoint(self.endpoint_json)
        self.bad_endpoint_json = ('{"callable": "func.ref", '
                                  '"argumentType": "arg.ref1", '
                                  '"returnType": "arg.ref2"}')


class GetSerializerForTests(WithEndpointTestMixin):
    def setUp(self):
        super().setUp()

    def test_passing_endpoint_json_works(self):
        serializer = self.client.get_serializer_for(self.endpoint_json)
        self.assertIsInstance(serializer, RpcProtobufSerializer)
        self.assertEqual(str(serializer.argument_type()), str(RpcRequestA))
        self.assertEqual(str(serializer.response_type()), str(RpcResponseA))

    def test_passing_endpoint_works(self):
        serializer = self.client.get_serializer_for(self.endpoint)
        self.assertIsInstance(serializer, RpcProtobufSerializer)
        self.assertEqual(str(serializer.argument_type()), str(RpcRequestA))
        self.assertEqual(str(serializer.response_type()), str(RpcResponseA))

    def test_passing_json_with_bad_class_references_does_not_raise(self):
        serializer = self.client.get_serializer_for(self.bad_endpoint_json)
        self.assertIsInstance(serializer, RpcProtobufSerializer)

    def test_raises_invalid_if_given_invalid_json(self):
        with self.assertRaises(InvalidArgumentError):
            self.client.get_serializer_for('this is not JSON')


class GetDefaultTimeoutSpecificationTests(BaseClientTestMixin):
    def test_default_timeout_spec_is_based_on_constructor_params(self):
        spec = self.client.get_default_timeout_specification()
        self.assertEqual(self.time_source.timeout_specification(10), spec)


class GetTimeoutSpecificationTests(WithEndpointTestMixin):
    def test_gets_client_default_when_endpoint_does_not_expose_a_default(self):
        self.assertFalse(hasattr(self.endpoint, 'get_default_timeout_specification'))
        self.assertFalse(hasattr(self.endpoint, 'get_timeout_specification'))
        # now we're sure it doesn't
        self.assertEqual(self.client.get_default_timeout_specification(),
                         self.client.get_timeout_specification(self.endpoint))

    def test_uses_the_endpoint_timeout_spec_if_has_one(self):
        mock_timeout = Mock()
        setattr(self.endpoint, 'get_timeout_specification', lambda: mock_timeout)
        self.assertEqual(mock_timeout, self.client.get_timeout_specification(self.endpoint))

    def test_uses_the_endpoint_default_timeout_spec_if_has_one(self):
        mock_timeout = Mock()
        setattr(self.endpoint, 'get_default_timeout_specification', lambda: mock_timeout)
        self.assertEqual(mock_timeout, self.client.get_timeout_specification(self.endpoint))

    def test_prefers_the_specific_over_the_default(self):
        mock_default_timeout = Mock()
        mock_timeout2 = Mock()
        setattr(self.endpoint, 'get_timeout_specification', lambda: mock_timeout2)
        setattr(self.endpoint, 'get_default_timeout_specification', lambda: mock_default_timeout)
        self.assertEqual(mock_timeout2, self.client.get_timeout_specification(self.endpoint))


class ClockForTests(BaseClientTestMixin):
    pass  # fixme: TBD implement this
