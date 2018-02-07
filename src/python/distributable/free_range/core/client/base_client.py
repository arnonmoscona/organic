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
        # fixme: documentation
        # fixme: note that default timeout is a number, not a spec
        if transport is None:
            raise InvalidArgumentError('None is not a valid transport')
        self._transport = transport
        self._time_source = time_source or TimeSource()
        timeout_specification = self._time_source.timeout_specification(default_timeout)
        self._time_source.validate_timeout_specification(timeout_specification)
        self. _default_timeout = default_timeout
        # todo: plugguble serializers

    def generate_call_id(self):
        return uuid4()  # a simple random UUID

    def get_serializer_for(self, endpoint):
        """
        Produces a serializer for the classes in the given endpoint
        :param endpoint: either a JSON string type reference, or an Endpoint instance
        :return: the appropriate type of serializer for the specified endpoint.
                Note that the seriallizer returned does not necessarily verify its input at this
                stage. It typically does not until its import_types() method is called.
        """
        return _serializer_for(endpoint)

    def route(self, endpoint, args):
        pass  # fixme: TBD implement this

    def get_timeout_specification(self, endpoint):
        # either from configuration or from default
        pass  # fixme: TBD implement this

    def get_timestamp(self):
        return self._time_source.timestamp()

    @property
    def transport(self):
        return self._transport

    def clock_for(self, timeout_spec):
        return TimeoutClock(timeout_spec)


@singledispatch
def _serializer_for(endpoint):
    raise InvalidArgumentError(f'No implementation of serializer_for for type {type(endpoint)}')


@lru_cache(maxsize=MEMOISE_CACHE_SIZE)
@_serializer_for.register(str)
def _serializer_from_string(endpoint_json):
    rpc_endpoint = RpcEndpoint(endpoint_json)
    return _serializer_for(rpc_endpoint)


@lru_cache(maxsize=MEMOISE_CACHE_SIZE)
@_serializer_for.register(RpcEndpoint)
def _serializer_from_rpc_endpoint(rpc_endpoint):
    arg_type = rpc_endpoint.argument_type_reference_string
    return_type = rpc_endpoint.return_type_reference_string
    return RpcProtobufSerializer(arg_type, return_type)
