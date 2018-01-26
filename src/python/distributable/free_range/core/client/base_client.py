"""
Common functionality for all aspects of client
"""
from uuid import uuid4

from free_range.core.common.exceptions import InvalidArgument
from free_range.core.common.time import TimeSource, TimeoutClock


class BaseClient:
    def __init__(self, transport, time_source=None):
        if transport is None:
            raise InvalidArgument('None is not a valid transport')
        self._time_source = time_source or TimeSource()
        self._transport = transport

    def generate_call_id(self, endpoint):
        # question: should we require a string here?
        # question: is endpoint needed?
        return uuid4()  # a simple random UUID

    def get_serializer_for(self, endpoint):
        pass  # fixme: TBD implement this

    def route(self, endpoint, args):
        pass  # fixme: TBD implement this

    def get_timeout_specification(self, endpoint):
        pass  # fixme: TBD implement this

    def get_timestamp(self):
        return self._time_source.timestamp()

    @property
    def transport(self):
        return self._transport

    def clock_for(self, timeout_spec):
        return TimeoutClock(timeout_spec)
