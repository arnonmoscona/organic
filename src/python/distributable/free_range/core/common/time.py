"""
Common framework classes having to do with time and timeouts
"""
from datetime import datetime
from enum import Enum

from free_range.core.common.exceptions import (DisallowedInCurrentStateError,
                                               InvalidArgumentError)


class TimeUnit(Enum):
    MILLIS = 'millis'
    TICKS = 'ticks'


class TimeSource:
    """The default time source: based on datetime.now()"""

    def __init__(self, injected_source=None):
        """
        The constructor would normally create a simple timestamp based on datetime.now().
        Should you want something else (like a timezone aware timestamp) you may inject your own
        source with a callable.
        :param injected_source: an optional callable to get the value of timestamp()
        """
        self._injected = injected_source
        self._last_value = 0.0

    def timestamp(self):
        if self._injected:
            new_value = self._injected()
        else:
            new_value = datetime.now().timestamp() * 1000.0

        new_value = max(float(self._last_value), float(new_value))
        self._last_value = new_value
        return new_value

    @property
    def units(self):
        return TimeUnit.MILLIS

    def timeout_specification(self, timeout):
        return TimeoutSpecification(timeout, self.units)

    def validate_timeout_specification(self, timeout_specification):
        if timeout_specification.units != self.units:
            raise InvalidArgumentError(f'timeout specification with incorrect units. '
                                       f'Expected {self.units} but got '
                                       f'{timeout_specification.units}')
        if timeout_specification.timeout < 0:
            raise InvalidArgumentError(f'timeout may not be negative. Got {timeout_specification}')


class _UselessTickCoordinator:
    """
    A tick coordinator that does not coordinate
    """

    def __init__(self):
        self._now = 0

    def now(self):
        return self._now

    def advance(self, count=1):
        self._now += max(count, 1)
        return self._now


class TickTimeSource:
    """
    A time source that is code-controlled.
    Uses natural number 'ticks' as a unit
    Intended for use in tests.
    """

    def __init__(self, coordinator=None):
        """
        Creates a new tick time source. The resulting time source would actually use a tick
        coordinator as the "real tick source". The inten t is to have a network coordinated
        tick source to allow for a testing environment with well defined, but inefficient event
        ordering
        :param coordinator: the real tick source to use. If None then and internal "useless
            coordinator" will be used. It is useless in that it does not
            actually coordinate anything.
        """
        self._coordinator = coordinator or _UselessTickCoordinator()
        self._current_time = self._coordinator.now()
        self._should_auto_advance = False
        self._next_advance_is_auto = False  # this helps behavior to be more intuitive

    @property
    def units(self):
        return TimeUnit.TICKS

    def timeout_specification(self, timeout):
        return TimeoutSpecification(timeout, self.units)

    def timestamp(self):
        if self._should_auto_advance:
            if self._next_advance_is_auto:
                self._current_time = self._coordinator.advance(1)
            self._next_advance_is_auto = True

        return self._current_time

    def advance(self, count=1):
        """
        Advances the time tick by the number of ticks provided.
        :param count: a number of at least 1, which indicates the number
            of whole ticks to add to the current timestamp
        :return: self. So you may say my_ts.advance(2).timestamp()
        """
        if int(count) < 1:
            raise InvalidArgumentError('Tick time source may only be advanced by positive values')
        self._current_time = self._coordinator.advance(int(count))
        self._next_advance_is_auto = False
        return self

    def auto_advance(self, state):
        self._should_auto_advance = state
        self._next_advance_is_auto = self._should_auto_advance
        return self

    def validate_timeout_specification(self, timeout_specification):
        if timeout_specification.units != self.units:
            raise InvalidArgumentError(f'timeout specification with incorrect units. '
                                       f'Expected {self.units} but got '
                                       f'{timeout_specification.units}')
        if timeout_specification.timeout < 0:
            raise InvalidArgumentError(f'timeout may not be negative. Got {timeout_specification}')


class TimeoutSpecification:
    """
    Represents a specified timeout. This can be present in configuration as well as
    in client API methods, such as async_request(). Timeouts are typically specified in
    milliseconds.
    Technically, they are expressed as "time source ticks" which are always milliseconds except
    when a specialized network coordinated tme source is used in testing.
    """

    def __init__(self, timeout, units=TimeUnit.MILLIS):
        """
        Specifies a timeout with units
        :param timeout: the timeout. A non-negative number or -1 to designate blocking call
        :param time_unit: the time unit to use. Should match the time source time unit
        """
        if not timeout or int(timeout) < 0 and int(timeout) != -1:
            raise InvalidArgumentError(f'timeout must be positive or -1 got: {timeout}')
        self.timeout = timeout
        self.units = units

    def __str__(self):
        return f'TimeoutSpecification({self.timeout} {self.units.value})'

    @property
    def is_blocking(self):
        return int(self.timeout) == -1

    def __eq__(self, other):
        return (isinstance(self, type(other))
                and self.units == other.units and self.timeout == other.timeout)


class TimeoutClock:
    def __init__(self, timeout_spec, time_source):
        self._timeout_spec = timeout_spec
        self._time_source = time_source
        self._start_time = None

    def __str__(self):
        return f'TimeoutClock(started_at: {self._start_time}), ' \
               f'timeout={self._timeout_spec.timeout}'

    def start(self):
        if self._start_time is not None:
            raise DisallowedInCurrentStateError(f'Clock already started at {self._start_time} '
                                                f'{self._timeout_spec.units.value}')
        self._start_time = self._time_source.timestamp()
        return self

    def is_expired(self):
        if self._start_time is None:
            return False

        return self.elapsed_time() >= self._timeout_spec.timeout

    def remaining_timeout_spec(self):
        if self._start_time is None:
            return None
        remaining_time = self._timeout_spec.timeout - self.elapsed_time()
        if remaining_time <= 0:
            raise TimeoutError('The specified timeout of {} has expired'.format(self._timeout_spec))
        return self._time_source.timeout_specification(remaining_time)

    def elapsed_time(self):
        if self._start_time is None:
            return 0
        return self._time_source.timestamp() - self._start_time
