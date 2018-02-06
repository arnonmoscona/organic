from unittest import TestCase

from free_range.core.common.endpoints import RpcEndpoint
from free_range.core.common.exceptions import InvalidArgumentError


class RpcEndPointConstructorTests(TestCase):
    def tearDown(self):
        RpcEndpoint.set_option_strict(False)

    def test_rpc_endpoint_can_be_constructed_with_a_string(self):
        RpcEndpoint('{"callable": "func.ref", "argumentType": "arg.ref1", '
                    '"returnType": "arg.ref2"}')

    def test_rpc_endpoint_can_be_constructed_with_an_argument_type(self):
        RpcEndpoint('{"callable": "func.ref", "argumentType": "arg.ref1"}')

    def test_rpc_endpoint_can_have_both_argument_and_return_types(self):
        RpcEndpoint('{"callable": "func.ref", "argumentType": "arg.ref1", '
                    '"returnType": "arg.ref2"}')

    def test_constructor_allows_function_only(self):
        RpcEndpoint('{"callable": "func.ref"}')

    def test_constructor_allows_function_and_return_type(self):
        RpcEndpoint('{"callable": "func.ref", "returnType": "arg.ref2"}')

    def test_a_function_reference_is_required(self):
        with self.assertRaises(InvalidArgumentError):
            RpcEndpoint('{}')

    def test_a_valid_json_is_required(self):
        with self.assertRaises(InvalidArgumentError):
            RpcEndpoint('bla')

    def test_does_not_check_whether_the_function_reference_is_sensible(self):
        RpcEndpoint('{"callable": "  "}')

    def test_in_strict_mode_function_reference_must_be_sensible1(self):
        RpcEndpoint.set_option_strict(True)
        with self.assertRaises(InvalidArgumentError):
            RpcEndpoint('{"callable": "  "}')

    def test_in_strict_mode_function_reference_must_be_sensible2(self):
        RpcEndpoint.set_option_strict(True)
        with self.assertRaises(InvalidArgumentError):
            RpcEndpoint('{"callable": "aaa!bbb"}')

    def test_in_strict_mode_function_reference_must_be_sensible3(self):
        RpcEndpoint.set_option_strict(True)
        with self.assertRaises(InvalidArgumentError):
            RpcEndpoint('{"callable": "aaa bbb"}')

    def test_in_strict_mode_function_reference_must_be_sensible4(self):
        RpcEndpoint.set_option_strict(True)
        with self.assertRaises(InvalidArgumentError):
            RpcEndpoint('{"callable": "aaa()"}')

    def test_in_strict_mode_arg_type_reference_must_be_sensible1(self):
        RpcEndpoint.set_option_strict(True)
        with self.assertRaises(InvalidArgumentError):
            RpcEndpoint('{"callable": "a", "argumentType": "  "}')

    def test_in_strict_mode_arg_type_reference_must_be_sensible2(self):
        RpcEndpoint.set_option_strict(True)
        with self.assertRaises(InvalidArgumentError):
            RpcEndpoint('{"callable": "a", "argumentType": "aaa bbb"}')

    def test_in_strict_mode_arg_type_reference_must_be_sensible3(self):
        RpcEndpoint.set_option_strict(True)
        with self.assertRaises(InvalidArgumentError):
            RpcEndpoint('{"callable": "a", "argumentType": "aaa!bbb"}')

    def test_in_strict_mode_arg_type_reference_must_be_sensible4(self):
        RpcEndpoint.set_option_strict(True)
        with self.assertRaises(InvalidArgumentError):
            RpcEndpoint('{"callable": "a", "argumentType": "a(X)"}')

    def test_in_strict_mode_return_type_reference_must_be_sensible1(self):
        RpcEndpoint.set_option_strict(True)
        with self.assertRaises(InvalidArgumentError):
            RpcEndpoint('{"callable": "a", "returnType": "  "}')

    def test_in_strict_mode_return_type_reference_must_be_sensible2(self):
        RpcEndpoint.set_option_strict(True)
        with self.assertRaises(InvalidArgumentError):
            RpcEndpoint('{"callable": "a", "returnType": "aaa bbb"}')

    def test_in_strict_mode_return_type_reference_must_be_sensible3(self):
        RpcEndpoint.set_option_strict(True)
        with self.assertRaises(InvalidArgumentError):
            RpcEndpoint('{"callable": "a", "returnType": "aaa!bbb"}')

    def test_in_strict_mode_return_type_reference_must_be_sensible4(self):
        RpcEndpoint.set_option_strict(True)
        with self.assertRaises(InvalidArgumentError):
            RpcEndpoint('{"callable": "a", "returnType": "a(X)"}')

    def test_in_strict_mode_underscores_are_ok(self):
        RpcEndpoint.set_option_strict(True)
        RpcEndpoint('{"callable": "a_b"}')

    def test_in_strict_mode_dot_separators_are_ok(self):
        RpcEndpoint.set_option_strict(True)
        RpcEndpoint('{"callable": "a.b"}')

    def test_in_strict_mode_leading_dot_separators_are_not_ok(self):
        RpcEndpoint.set_option_strict(True)
        with self.assertRaises(InvalidArgumentError):
            RpcEndpoint('{"callable": ".a"}')

    def test_in_strict_mode_trailing_dot_separators_are_not_ok(self):
        RpcEndpoint.set_option_strict(True)
        with self.assertRaises(InvalidArgumentError):
            RpcEndpoint('{"callable": "a."}')

    def test_in_strict_mode_consecutive_dot_separators_are_not_ok(self):
        RpcEndpoint.set_option_strict(True)
        with self.assertRaises(InvalidArgumentError):
            RpcEndpoint('{"callable": "a..b"}')

    def test_set_option_strict_can_be_reverted(self):
        RpcEndpoint.set_option_strict(True)
        RpcEndpoint.set_option_strict(False)
        RpcEndpoint('{"callable": "a", "returnType": "a(X)"}')


class SimpleTestMixin(TestCase):
    def setUp(self):
        self.end_point = RpcEndpoint('{"callable": "func", "argumentType": "Arg", '
                                     '"returnType": "ReturnValueType"}')


class FunctionReferenceStringTests(SimpleTestMixin):
    def test_returns_the_function_component(self):
        self.assertEqual('func', self.end_point.function_reference_string)


class ArgumentTypeReferenceStringTests(SimpleTestMixin):
    def test_returns_the_argument_type_component(self):
        self.assertEqual('Arg', self.end_point.argument_type_reference_string)


class ReturnTypeReferenceStringTests(SimpleTestMixin):
    def test_returns_the_return_type_component(self):
        self.assertEqual('ReturnValueType', self.end_point.return_type_reference_string)


class PatternTests(SimpleTestMixin):
    def test_pattern_is_rpc(self):
        self.assertEqual('RPC', self.end_point.pattern)


class UniqueReferenceTests(SimpleTestMixin):
    def test_unique_reference_is_pattern_and_callable(self):
        self.assertEqual('RPC:func', self.end_point.unique_reference)
