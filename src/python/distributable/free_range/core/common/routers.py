"""
endpoint and message routers
"""
from abc import ABC, abstractmethod


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
        raise NotImplementedError()


class LocalStackRouter(EndpointRouter):
    def route(self, endpoint, message=None):
        pass  # fixme: TBD implement this
