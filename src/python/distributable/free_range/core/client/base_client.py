"""
Common functionality for all aspects of client
"""
from uuid import uuid4

from free_range.core.common.exceptions import InvalidArgument
from free_range.core.common.time import TimeSource, TimeoutClock


class BaseClient:
    def __init__(self, transport, default_timeout, time_source=None):
        # fixme: documentation, type hints
        # fixme: note that default timeout is a number, not a spec
        if transport is None:
            raise InvalidArgument('None is not a valid transport')
        self._transport = transport
        self._time_source = time_source or TimeSource()
        timeout_specification = self._time_source.timeout_specification(default_timeout)
        self._time_source.validate_timeout_specification(timeout_specification)
        self. _default_timeout = default_timeout

    def generate_call_id(self):
        return uuid4()  # a simple random UUID

    def get_serializer_for(self, endpoint):
        pass  # fixme: TBD implement this

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
