"""
Common functionality for all aspects of client
"""
from free_range.core.common.time import TimeSource, TimeoutClock


class BaseClient:
    def __init__(self, transport, time_source=None):
        self._time_source = time_source or TimeSource()
        self._transport = transport

    def generate_call_id(self, endpoint):
        pass  # fixme: TBD implement this

    def get_serializer_for(self, endpoint):
        pass  # fixme: TBD implement this

    def route(self, endpoint, args):
        pass  # fixme: TBD implement this

    def get_timeout_spec(self, endpoint):
        pass  # fixme: TBD implement this

    def get_timestamp(self):
        return self._time_source.timestamp()

    @property
    def transport(self):
        return self._transport

    def clock_for(self, timeout_spec):
        return TimeoutClock(timeout_spec)
