"""
Common framework classes having to do with time and timeouts
"""
from datetime import datetime
from enum import Enum


class TimeUnit(Enum):
    MILLIS = 'millis'
    TICKS = 'ticks'


class TimeSource:
    """The default time source: based on datetime.now()"""

    def timestamp(self):
        return datetime.now().timestamp() * 1000.0

    @property
    def units(self):
        return TimeUnit.MILLIS


class TimeoutSpecification:
    """
    Represents a specified timeout. This can be present in configuration as well as
    in client API methods, such as async_request(). Timeouts are typically specified in
    milliseconds.
    Technically, they are expressed as "time source ticks" which are always milliseconds except
    when a specialized network coordinated tme source is used in testing.
    """
    pass  # fixme: timeout specification: time + time source

