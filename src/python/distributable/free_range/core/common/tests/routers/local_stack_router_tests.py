from unittest import TestCase
from unittest.mock import Mock

from free_range.core.client.tests.papi.rpc_test_papi_pb2 import (RpcRequestA,
                                                                 RpcResponseA)
from free_range.core.common.endpoints import PATTERN_RPC
from free_range.core.common.exceptions import (InvalidArgumentError,
                                               NotFoundError)
from free_range.core.common.routers import (LocalStackRouter,
                                            LocalStackRpcEndpointLocation)


def rpc_function(argument):
    return RpcResponseA(response=f'response to {argument.request}')


class LocalStackRouterTestMixin(TestCase):
    def setUp(self):
        self.package = 'free_range.core.common.tests.routers'
        self.endpoint = Mock()
        self.endpoint.pattern = PATTERN_RPC
        function_name = f'{self.package}.local_stack_router_tests.rpc_function'
        self.endpoint.function_reference_string = function_name
        self.router = LocalStackRouter()


class RouteTests(LocalStackRouterTestMixin):
    def test_route_returns_a_local_stack_location(self):
        self.assertIsInstance(self.router.route(self.endpoint), LocalStackRpcEndpointLocation)

    def test_can_get_a_callable(self):
        location = self.router.route(self.endpoint)
        self.assertTrue(callable(location.callable()))

    def test_callable_works(self):
        location = self.router.route(self.endpoint)
        response = location.callable()(RpcRequestA(request='r')).response
        self.assertEqual('response to r', response)

    def test_if_passing_a_bad_argument_raises_invalid(self):
        with self.assertRaises(InvalidArgumentError):
            self.router.route('some garbage')

    def if_passing_a_non_rpc_endpoint_raises_invalid(self):
        self.endpoint.pattern = 'not RPC'
        with self.assertRaises(InvalidArgumentError):
            self.router.route(self.endpoint)

    def if_function_is_not_importable_raises_not_found(self):
        self.endpoint.function_reference_string = f'{self.endpoint.function_reference_string}_xx'
        with self.assertRaises(NotFoundError):
            self.router.route(self.endpoint).callable()
