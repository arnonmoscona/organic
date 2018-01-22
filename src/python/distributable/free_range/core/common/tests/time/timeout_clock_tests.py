import unittest

from free_range.core.common.exceptions import DisallowedInCurrentStateError
from free_range.core.common.time import TickTimeSource, TimeoutClock


class TimeoutClockTestMixin(unittest.TestCase):
    def setUp(self):
        self.time_source = TickTimeSource()
        self.timeout_spec = self.time_source.timeout_specification(10)
        self.clock = TimeoutClock(self.timeout_spec, self.time_source)


class StartTests(TimeoutClockTestMixin):
    def test_can_only_start_once(self):
        self.clock.start()
        with self.assertRaises(DisallowedInCurrentStateError):
            self.clock.start()


class IsExpiredTests(TimeoutClockTestMixin):
    def test_if_the_clock_started_and_the_timeout_was_not_reached_then_is_expired_is_false(self):
        self.assertFalse((self.clock.start().is_expired()))
        self.time_source.advance(9)
        self.assertFalse((self.clock.is_expired()))

    def test_if_the_clock_started_and_the_timeout_was_reached_then_is_expired_is_true(self):
        self.clock.start()
        self.time_source.advance(10)
        self.assertTrue((self.clock.is_expired()))

    def test_if_the_clock_is_not_started_then_then_the_timeout_is_ignored(self):
        self.time_source.advance(10)
        self.assertFalse((self.clock.is_expired()))


class RemainingTimeoutTests(TimeoutClockTestMixin):
    def test_clock_produces_a_timeout_spec_with_remaining_time(self):
        self.clock.start()
        self.time_source.advance(3)
        spec = self.clock.remaining_timeout_spec()
        self.assertEqual(7, spec.timeout)

    def test_if_the_clock_is_not_started_none_is_returned(self):
        self.time_source.advance(3)
        spec = self.clock.remaining_timeout_spec()
        self.assertIsNone(spec)

    def test_if_the_timeout_expired_then_getting_remaining_timeout_raises_a_timeout_error(self):
        self.clock.start()
        self.time_source.advance(10)
        with self.assertRaises(TimeoutError):
            self.clock.remaining_timeout_spec()


class ElapsedTimeTests(TimeoutClockTestMixin):
    def test_an_unstarted_clock_returns_zero_elapsed_time(self):
        self.assertEqual(0, self.clock.elapsed_time())

    def test_once_started_elapsed_time_is_measured_from_the_time_start_was_called(self):
        self.time_source.advance(12)
        self.clock.start()
        self.time_source.advance(4)
        self.assertEqual(4, self.clock.elapsed_time())

    def test_elapsed_time_can_be_checked_beyond_the_specified_timeout(self):
        self.clock.start()
        self.time_source.advance(20)
        self.assertEqual(20, self.clock.elapsed_time())
