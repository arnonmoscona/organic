import unittest
from unittest.mock import Mock

from free_range.core.client.tests.papi.rpc_test_papi_pb2 import (RpcRequestA,
                                                                 RpcResponseA)
from free_range.core.common.exceptions import (InvalidArgumentError,
                                               InvalidStateError,
                                               NotFoundError,
                                               SerializationError)
from free_range.core.common.serializers import (RpcProtobufSerializer,
                                                Serializer)


class RpcProtobufSerializerTestMixin(unittest.TestCase):
    def setUp(self):
        self.test_module_name = 'free_range.core.client.tests.papi.rpc_test_papi_pb2'
        self.rpc_request_a_name = f'{self.test_module_name}.RpcRequestA'
        self.rpc_response_a_name = f'{self.test_module_name}.RpcResponseA'


class RpcProtobufSerializerConstructorTests(RpcProtobufSerializerTestMixin):

    def test_constructor_works_with_type_name_arguments(self):
        RpcProtobufSerializer(self.rpc_request_a_name, self.rpc_response_a_name)

    def test_constructor_works_with_none_for_the_argument_type(self):
        RpcProtobufSerializer(None, self.rpc_response_a_name)

    def test_constructor_works_with_none_for_the_response_type(self):
        RpcProtobufSerializer(self.rpc_request_a_name, None)


class ImportTypesTests(RpcProtobufSerializerTestMixin):

    def test_import_valid_names_does_not_raise(self):
        serializer = RpcProtobufSerializer(self.rpc_request_a_name, self.rpc_response_a_name)
        serializer.import_types()

    def test_import_valid_names_does_not_raise_if_request_is_none(self):
        serializer = RpcProtobufSerializer(None, self.rpc_response_a_name)
        serializer.import_types()

    def test_import_valid_names_does_not_raise_if_response_is_none(self):
        serializer = RpcProtobufSerializer(self.rpc_request_a_name, None)
        serializer.import_types()

    def test_import_valid_names_does_not_raise_if_both_are_none(self):
        serializer = RpcProtobufSerializer(None, None)
        serializer.import_types()

    def test_import_raises_not_found_if_a_bad_arg_type_is_specified(self):
        serializer = RpcProtobufSerializer('bad.type', self.rpc_response_a_name)
        with self.assertRaises(NotFoundError):
            serializer.import_types()

    def test_import_raises_not_found_if_a_bad_response_type_is_specified(self):
        serializer = RpcProtobufSerializer(self.rpc_request_a_name, 'bad.type')
        with self.assertRaises(NotFoundError):
            serializer.import_types()


class ArgumentTypeTests(RpcProtobufSerializerTestMixin):
    def setUp(self):
        super().setUp()
        self.serializer = RpcProtobufSerializer(self.rpc_request_a_name, self.rpc_response_a_name)

    def test_returns_the_correct_type_if_imported(self):
        self.serializer.import_types()
        arg_type = self.serializer.argument_type()
        self.assertEqual('free_range.core.client.tests.papi.rpc_test_papi_pb2.RpcRequestA',
                         arg_type.DESCRIPTOR.full_name)

    def test_can_use_arg_type_as_the_type_you_expect(self):
        self.serializer.import_types()
        arg_type = self.serializer.argument_type()
        instance = arg_type()
        self.assertIsInstance(instance, RpcRequestA)
        # This is enough, but lets verify further...

        instance.request = 'some value'
        self.assertEqual('some value', instance.request)
        self.assertTrue(instance.IsInitialized())
        self.assertListEqual(['request'], list(instance.DESCRIPTOR.fields_by_name.keys()))

        instance2 = RpcRequestA()
        instance2.request = instance.request
        self.assertEqual(instance2, instance)

    def test_raises_if_not_imported(self):
        with self.assertRaises(InvalidStateError):
            self.serializer.argument_type(auto_import=False)

    def test_can_request_auto_import(self):
        arg_type = self.serializer.argument_type(auto_import=True)
        self.assertIsInstance(arg_type(), RpcRequestA)

    def test_returns_none_if_no_argument_specified(self):
        self.serializer = RpcProtobufSerializer(None, self.rpc_response_a_name)
        self.assertIsNone(self.serializer.argument_type(auto_import=True))


class ResponseTypeTests(RpcProtobufSerializerTestMixin):
    def setUp(self):
        super().setUp()
        self.serializer = RpcProtobufSerializer(self.rpc_request_a_name, self.rpc_response_a_name)

    def test_returns_the_correct_type_if_imported(self):
        self.serializer.import_types()
        arg_type = self.serializer.response_type()
        self.assertEqual('free_range.core.client.tests.papi.rpc_test_papi_pb2.RpcResponseA',
                         arg_type.DESCRIPTOR.full_name)

    def test_can_use_response_type_as_the_type_you_expect(self):
        self.serializer.import_types()
        resp_type = self.serializer.response_type()
        instance = resp_type()
        self.assertIsInstance(instance, RpcResponseA)
        # This is enough, but lets verify further...

        instance.response = 'some value'
        self.assertEqual('some value', instance.response)
        self.assertTrue(instance.IsInitialized())
        self.assertListEqual(['response'], list(instance.DESCRIPTOR.fields_by_name.keys()))

        instance2 = RpcResponseA()
        instance2.response = instance.response
        self.assertEqual(instance2, instance)

    def test_raises_if_not_imported(self):
        with self.assertRaises(InvalidStateError):
            self.serializer.response_type(auto_import=False)

    def test_can_request_auto_import(self):
        self.serializer.response_type(auto_import=True)

    def test_returns_none_if_no_response_type_specified(self):
        self.serializer = RpcProtobufSerializer(self.rpc_request_a_name, None)
        self.assertIsNone(self.serializer.response_type(auto_import=True))

    def test_returns_none_if_no_argument_type_specified(self):
        self.serializer = RpcProtobufSerializer(None, self.rpc_response_a_name)
        self.assertIsNone(self.serializer.argument_type(auto_import=True))


class ArgumentTypeSerializerTests(RpcProtobufSerializerTestMixin):
    def setUp(self):
        super().setUp()
        self.serializer = RpcProtobufSerializer(self.rpc_request_a_name, self.rpc_response_a_name)
        self.none_case = RpcProtobufSerializer(None, None)
        self.argument = RpcRequestA(request='something')

        # induce exceptions...
        fuse = Mock()
        fuse.side_effect = Exception('boom')
        self.bomb = RpcRequestA()
        self.bomb._fields = fuse

    def test_returns_a_serializer(self):
        serializer = self.serializer.argument_type_serializer()
        self.assertIsInstance(serializer, Serializer)

    def test_can_serialize_request(self):
        serialized = self.serializer.argument_type_serializer().serialize(self.argument)
        self.assertEqual(b'\n\tsomething', serialized)

    def test_can_serialize_an_empty_request(self):
        serialized = self.serializer.argument_type_serializer().serialize(RpcRequestA())
        self.assertEqual(b'', serialized)

    def test_treats_none_as_empty_request(self):
        serialized = self.serializer.argument_type_serializer().serialize(None)
        self.assertEqual(b'', serialized)

    def test_passing_the_wrong_type_raises_invalid(self):
        with self.assertRaises(InvalidArgumentError):
            self.serializer.argument_type_serializer().serialize(RpcResponseA())

    def test_can_deserialize_request(self):
        request = self.serializer.argument_type_serializer().deserialize(b'\n\tsomething')
        self.assertEqual(self.argument, request)

    def test_deserializing_none_raises_invalid(self):
        with self.assertRaises(InvalidArgumentError):
            self.serializer.argument_type_serializer().deserialize(None)

    def test_deserializing_not_bytes_raises_invalid(self):
        with self.assertRaises(InvalidArgumentError):
            self.serializer.argument_type_serializer().deserialize(RpcRequestA())

    def test_deserializing_an_empty_message_results_in_empty_byte_array(self):
        request = self.serializer.argument_type_serializer().deserialize(b'')
        self.assertEqual(RpcRequestA(), request)

    def test_serialize_raises_invalid_if_no_argument_type(self):
        with self.assertRaises(InvalidArgumentError):
            self.none_case.argument_type_serializer().serialize(RpcRequestA(request='something'))

    def test_deserialize_raises_invalid_if_no_response_type(self):
        with self.assertRaises(InvalidArgumentError):
            self.none_case.argument_type_serializer().deserialize(b'')

    def test_wraps_exceptions_in_exception_error(self):
        with self.assertRaises(SerializationError):
            self.serializer.argument_type_serializer().serialize(self.bomb)


class ResponseTypeSerializerTests(RpcProtobufSerializerTestMixin):
    # Note: this is basically the same as ArgumentTypeSerializerTests
    #       so only doing basic tests here as te rest is covered by ArgumentTypeSerializerTests
    def setUp(self):
        super().setUp()
        self.serializer = RpcProtobufSerializer(self.rpc_request_a_name, self.rpc_response_a_name)
        self.none_case = RpcProtobufSerializer(None, None)
        self.response = RpcResponseA(response='hello')

    def test_returns_a_serializer(self):
        serializer = self.serializer.response_type_serializer()
        self.assertIsInstance(serializer, Serializer)

    def test_can_serialize_response(self):
        serialized = self.serializer.response_type_serializer().serialize(self.response)
        self.assertEqual(b'\n\x05hello', serialized)

    def test_can_deserialize_response(self):
        response = self.serializer.response_type_serializer().deserialize(b'\n\x05hello')
        self.assertEqual(self.response, response)
