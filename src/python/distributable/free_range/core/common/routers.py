"""
endpoint and message routers
"""
from abc import ABC, abstractmethod

from free_range.core.common import dynamic
from free_range.core.common.decorators import public_interface
from free_range.core.common.endpoints import PATTERN_RPC
from free_range.core.common.exceptions import InvalidArgumentError


class EndpointRouter(ABC):
    @abstractmethod
    def route(self, endpoint, message=None):
        """
        This method takes an endpoint, or an endpoint specification and calls thr message
        router to resolve the endpoint into a usable EndpointLocation that includes also the
        routing information of where to find the endpoint in the network.
        :param endpoint: the endpoint to route
        :param message: and optional message that may be used by the message router.
            A message router may be content aware and may use the message contents to
            decide which route to use. For instance, it may use a partitioning scheme of some kind.
        :return: a EndpointLocation, which includes the routing information. Note that the local
            stack using the local transport is a valid remote endpoint as is some endpoint
            that resides on the the same machine (localhost or loopback address).
        """
        raise NotImplementedError('Attempt to invoke abstacrt EndpointRouter.rount()')


class LocalStackRouter(EndpointRouter):
    @public_interface
    def route(self, endpoint, message=None):
        """
        Returns a local location as appropriate for the endpoint pattern
        :param EndPoint endpoint: an endpoint descriptor
        :param message: an optional message (not used in the local case)
        :return: an EndpointLocation that can subsequenctly be used by a local transport
        :rtype EndpointLocation:
        """
        return LocalStackRpcEndpointLocation(endpoint)


class EndpointLocation(ABC):
    """
    Represents a resolved location of an endpoint, which can be invoked in the way that is
    appropriate for the endpoint type.
    """

    # fixme: add abstract methods for callable and get_endpoint


class LocalStackRpcEndpointLocation(EndpointLocation):
    """
    Calls and RPC endpoint locally. To call the function specified in the endpoint mst be
    importable locally.
    """

    @public_interface
    def __init__(self, endpoint):
        """
        :param EndPoint endpoint: the endpoint to use. Not a JSON descriptor.
        """
        try:
            if endpoint.pattern != PATTERN_RPC:
                raise InvalidArgumentError('LocalStackRpcEndpointLocation instantiated with en '
                                           'endpoint of the wrong pattern. '
                                           f'Expected "{PATTERN_RPC}" and got "{endpoint.pattern}"')
        except AttributeError:
            raise InvalidArgumentError('Was not able to determine endpoint pattern.')
        self._endpoint = endpoint

    @public_interface
    def callable(self):
        """
        Imports the function described by the RPC endpoint and returns a reference to the callable.
        The local transport uses this callable to actually invoke the function as an RPC request
        :return: A locally callble function
        :raises NotFoundError: if the function is not importable or not on the Python path
        :raises InvalidArgumentError: if there are problems with the endpoint descriptor itself
            or with the structure of the function reference string
        """
        try:
            function_ref = self._endpoint.function_reference_string
            return dynamic.import_by_name(function_ref, require_callable=True)
        except AttributeError:
            raise InvalidArgumentError(f'Could not mport function from {self._endpoint}')

    @public_interface
    def get_endpoint(self):
        # fixme: document and test this
        return self._endpoint
