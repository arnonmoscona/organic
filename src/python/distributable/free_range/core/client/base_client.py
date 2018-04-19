"""
Common functionality for all aspects of client
"""
from functools import lru_cache, singledispatch
from uuid import uuid4

from free_range.core.common.decorators import public_interface
from free_range.core.common.endpoints import RpcEndpoint
from free_range.core.common.exceptions import InvalidArgumentError
from free_range.core.common.routers import LocalStackRouter
from free_range.core.common.serializers import RpcProtobufSerializer
from free_range.core.common.time import TimeoutClock, TimeSource

MEMOISE_CACHE_SIZE = 1000

# OR-5: type hints


class BaseClient:  # fixme: inherit from Resolver(ABC)
    @public_interface
    def __init__(self, transport, default_timeout, time_source=None):
        """
        Creates a a basic free_range client. This serves as the main entry point into free_range
        functionality. The client acts as a factory for various other free_range objects that
        facilitate communication, e.g. RPC endpoints, message serializers, timeout specifications
        etc. While several of these objects can be created directly, creating them via the client
        makes it easier to ensure that they all share some important elements, such as a
        common time source.

        :param transport: the message transport to use. You may use multiple transports in
            the same application, but this is the default transport that would be used in
            factory methods.
        :param default_timeout: the unitless default timeout. The units are desived from the
            timesource. Must be a  non-negative number.
        :param time_source: The timesource to use. If not provided then
            free_range.core.common.time.TimeSource is used.
            :raises InvalidArgumentError: if any of the arguments is checked and is invalid.
                e.g. if the timeout is negative.
        """
        if transport is None:
            raise InvalidArgumentError('None is not a valid transport')
        self._transport = transport
        self._time_source = time_source or TimeSource()
        timeout_specification = self._time_source.timeout_specification(default_timeout)
        self._time_source.validate_timeout_specification(timeout_specification)
        invalid_timeout_err = InvalidArgumentError('Must provide a default timeout '
                                                   '(non-negative number)')
        if default_timeout is None:
            raise invalid_timeout_err
        try:
            self. _default_timeout = float(default_timeout)
            if self._default_timeout < 0:
                raise invalid_timeout_err
        except TypeError:
            raise invalid_timeout_err

        self._router = LocalStackRouter()
        # todo: plugguble serializers

    @public_interface
    def generate_call_id(self):
        return uuid4()  # a simple random UUID

    @public_interface
    def get_serializer_for(self, endpoint):
        """
        Produces a serializer for the classes in the given endpoint
        :param endpoint: either a JSON string endpoint reference, or an Endpoint instance
        :return: the appropriate type of serializer for the specified endpoint.
                Note that the seriallizer returned does not necessarily verify its input at this
                stage. It typically does not until its import_types() method is called.
        """
        return _serializer_for(endpoint)

    @public_interface
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
        self._router.route(endpoint, message)

    @public_interface
    def get_default_timeout_specification(self):
        """
        Produces a timeout specification from the default timeout numeric value and the
        units of the time source.
        :return: a TimeoutSpecification
        """
        return self._time_source.timeout_specification(self._default_timeout)

    @public_interface
    def get_timeout_specification(self, endpoint):
        """
        Gets a timeout specification. The function will get the timeout specification from the
        the provided endpoint if it cas. It first tries tries to call get_timeout_specification()
        on the endpoint. If it succeeds then that is the return value. If it fails *for any reason*
        then it will try to return get_default_timeout_specification() from the endpoint.
        Failing to to do that it will return the client's default timeout specification.
        Note that in the process this method can swallow exceptions. It puts a priority
        on getting some reasonable timeout specification over exposing every issue it encounters.
        Specifically, the endpoint can be a JSON string specifying the endpoint. If it cannot make
        an edpoint from that, then it falls back on the default. The function also uses duck
        typing on an endpoint instance. Any object that responds to get_timeout_specification()
        or to get_default_timeout_specification() is treated as a valid timeout sepecification
        provider.

        InvalidArgumentError is swallowed.
        AttributeError that occurs when calling the endpoint timeout functions is also
        swallowed (duck typing: method not present is OK. We move on)
        :param endpoint: an object that may respond to one of the two timeout specification
            methods or a JSON string specifying an endpoint.
        :return: whatever the endpoint responded with. It does not validate the return value,
            or the default timeout specification of the client.
        """
        try:
            endpoint_timeout = _get_timeout_specification_of(_endpoint_for(endpoint))
        except InvalidArgumentError:
            endpoint_timeout = None
        return endpoint_timeout or self.get_default_timeout_specification()

    @public_interface
    def get_timestamp(self):
        return self._time_source.timestamp()

    @property
    @public_interface
    def transport(self):
        return self._transport

    @public_interface
    def clock_for(self, timeout_spec):
        """
        A factory method for a timeout clock
        :param timeout_spec: any TimeoutSpecification
        :return: A new TimeoutClock
        :raises AttributeError or ValueError: if the timeout specification object or
            the time source don't behave as expected. This only happens if non-framework
            objects are provided. You should get no exception with the appropriate Free Range
            types.
        """
        return TimeoutClock(timeout_spec, self._time_source)


@singledispatch
def _serializer_for(endpoint):
    raise InvalidArgumentError(f'No implementation of serializer_for for type {type(endpoint)}')


@lru_cache(maxsize=MEMOISE_CACHE_SIZE)
@_serializer_for.register(str)
def _serializer_for_str(endpoint_json):
    endpoint = _endpoint_for(endpoint_json)
    return _serializer_for(endpoint)


@lru_cache(maxsize=MEMOISE_CACHE_SIZE)
@_serializer_for.register(RpcEndpoint)
def _serializer_for_rpc_endpoint(rpc_endpoint):
    arg_type = rpc_endpoint.argument_type_reference_string
    return_type = rpc_endpoint.return_type_reference_string
    return RpcProtobufSerializer(arg_type, return_type)


@singledispatch
def _endpoint_for(endpoint):
    raise InvalidArgumentError(f'Cannot produce endpoint from {endpoint}')


@_endpoint_for.register(RpcEndpoint)
def _endpoint_for_rpc_endpoint(endpoint):
    return endpoint


@lru_cache(maxsize=MEMOISE_CACHE_SIZE)
@_endpoint_for.register(str)
def _endpoint_for_str(endpoint_spec):
    try:
        return RpcEndpoint(endpoint_spec)  # todo: other endpoint types
    except Exception as ex:
        raise InvalidArgumentError(f'Cannot produce endpoint from {endpoint_spec}',
                                   caused_by=ex)


def _get_timeout_specification_of(thing):
    try:
        return thing.get_timeout_specification()
    except AttributeError:
        try:
            return thing.get_default_timeout_specification()
        except AttributeError:
            return None
