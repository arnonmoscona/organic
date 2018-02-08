"""
Common functionality for all aspects of client
"""
from functools import lru_cache, singledispatch
from uuid import uuid4

from free_range.core.common.endpoints import RpcEndpoint
from free_range.core.common.exceptions import InvalidArgumentError
from free_range.core.common.serializers import RpcProtobufSerializer
from free_range.core.common.time import TimeoutClock, TimeSource

MEMOISE_CACHE_SIZE = 1000

# OR-5: type hints


class BaseClient:
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
        # todo: plugguble serializers

    def generate_call_id(self):
        return uuid4()  # a simple random UUID

    def get_serializer_for(self, endpoint):
        """
        Produces a serializer for the classes in the given endpoint
        :param endpoint: either a JSON string endpoint reference, or an Endpoint instance
        :return: the appropriate type of serializer for the specified endpoint.
                Note that the seriallizer returned does not necessarily verify its input at this
                stage. It typically does not until its import_types() method is called.
        """
        return _serializer_for(endpoint)

    def route(self, endpoint, args):
        pass  # fixme: TBD implement this

    def get_default_timeout_specification(self):
        return self._time_source.timeout_specification(self._default_timeout)

    def get_timeout_specification(self, endpoint):
        # either from configuration or from default
        try:
            endpoint_timeout = _get_timeout_specification_of(_endpoint_for(endpoint))
        except InvalidArgumentError:
            endpoint_timeout = None
        return endpoint_timeout or self.get_default_timeout_specification()

    def get_timestamp(self):
        return self._time_source.timestamp()

    @property
    def transport(self):
        return self._transport

    def clock_for(self, timeout_spec):
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
