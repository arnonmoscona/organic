import unittest
from unittest import mock

from free_range.core.common.exceptions import InvalidArgument
from free_range.core.common.tests.random_mixin import RandomMixin
from free_range.core.common.time import (TickTimeSource, TimeUnit, TimeoutSpecification)


class UnitsTests(unittest.TestCase):
    def test_unit_is_ticks(self):
        self.assertEqual(TimeUnit.TICKS, TickTimeSource().units)


class TimeStampTests(unittest.TestCase):
    def test_timestamps_start_at_zero(self):
        self.assertEqual(0, TickTimeSource().timestamp())


class AdvanceTests(RandomMixin, unittest.TestCase):
    def setUp(self):
        self.time_source = TickTimeSource()

    def test_advance_defaults_to_advancing_by_one(self):
        ts1 = self.time_source.timestamp()
        ts2 = self.time_source.advance().timestamp()
        self.assertEqual(1, ts2 - ts1)

    def test_advance_by_a_number_advances_as_specified(self):
        ts1 = self.time_source.timestamp()
        amount = self.random_natural()
        ts2 = self.time_source.advance(amount).timestamp()
        self.assertEqual(amount, ts2 - ts1)

    def test_trying_to_advance_by_zero_fails(self):
        with self.assertRaises(InvalidArgument):
            self.time_source.advance(0).timestamp()

    def test_trying_to_advance_by_negative_fails(self):
        with self.assertRaises(InvalidArgument):
            self.time_source.advance(-10).timestamp()

    def test_trying_to_advance_by_float_converts_to_integer(self):
        ts1 = self.time_source.timestamp()
        ts2 = self.time_source.advance(2.6).timestamp()
        self.assertEqual(2, ts2 - ts1)


class CoordinatorTests(RandomMixin, unittest.TestCase):
    def setUp(self):
        self.coordinator = mock.Mock()
        self.coordinator.timeout = mock.Mock()
        self.random_timestamp = self.random_natural()
        self.coordinator.now.return_value = self.random_timestamp
        self.coordinator.advance = mock.Mock()
        self.time_source = TickTimeSource(coordinator=self.coordinator)

    def test_coordinator_is_consulted_for_timestamp(self):
        ts = self.time_source.timestamp()
        self.assertEqual(self.random_timestamp, ts)
        self.coordinator.now.assert_called_once()

    def test_coordinator_is_consulted_for_advance(self):
        self.time_source.advance()
        self.coordinator.advance.assert_called_once()

    def test_coordinator_advance_method_called_with_same_value(self):
        self.time_source.advance(10)
        self.coordinator.advance.assert_called_once_with(10)


class TimeoutSpecificationTests(unittest.TestCase):
    def test_creating_a_timeout_spec_produces_one_with_tick_units(self):
        self.assertEqual(TimeUnit.TICKS, TickTimeSource().timeout_specification(10).units)

    def test_creating_a_timeout_spec_reflects_the_argument(self):
        tos = TickTimeSource().timeout_specification(10)
        self.assertEqual((10, TimeUnit.TICKS), (tos.timeout, tos.units))


class AutoAdvanceTests(unittest.TestCase):
    def test_auto_advance_returns_self(self):
        ts = TickTimeSource()
        self.assertEqual(ts, ts.auto_advance(False))

    def test_when_auto_advance_is_on_timestamp_increases_on_each_call(self):
        time_source = TickTimeSource().auto_advance(True)
        ts1 = time_source.timestamp()
        ts2 = time_source.timestamp()
        ts3 = time_source.timestamp()
        time_source.advance(5)
        ts4 = time_source.timestamp()
        ts5 = time_source.timestamp()

        expected = [1, 2, 3, 8, 9]
        actual = [ts1, ts2, ts3, ts4, ts5]
        self.assertEqual(expected, actual)

    def test_when_auto_advance_is_off_then_advances_only_explicitly(self):
        time_source = TickTimeSource().auto_advance(False)
        ts1 = time_source.timestamp()
        ts2 = time_source.timestamp()
        ts3 = time_source.timestamp()
        time_source.advance(5)
        ts4 = time_source.timestamp()
        ts5 = time_source.timestamp()

        expected = [0, 0, 0, 5, 5]
        actual = [ts1, ts2, ts3, ts4, ts5]
        self.assertEqual(expected, actual)

    def test_can_turn_off_auto_advance_midway(self):
        time_source = TickTimeSource().auto_advance(True)
        ts1 = time_source.timestamp()
        ts2 = time_source.timestamp()
        time_source.auto_advance(False)
        ts3 = time_source.timestamp()
        time_source.advance(5)
        ts4 = time_source.timestamp()
        ts5 = time_source.timestamp()

        expected = [1, 2, 2, 7, 7]
        actual = [ts1, ts2, ts3, ts4, ts5]
        self.assertEqual(expected, actual)

    def test_can_turn_on_auto_advance_midway(self):
        time_source = TickTimeSource().auto_advance(False)
        ts1 = time_source.timestamp()
        ts2 = time_source.timestamp()
        time_source.auto_advance(True)
        ts3 = time_source.timestamp()
        time_source.advance(5)
        ts4 = time_source.timestamp()
        ts5 = time_source.timestamp()

        expected = [0, 0, 1, 6, 7]
        actual = [ts1, ts2, ts3, ts4, ts5]
        self.assertEqual(expected, actual)


class ValidateTimeoutSpecificationTests(unittest.TestCase):
    def setUp(self):
        self.time_source = TickTimeSource()

    def test_correct_units_and_positive_timeout_is_valid(self):
        self.time_source.validate_timeout_specification(self.time_source.timeout_specification(1))

    def test_correct_units_and_negative_timeout_is_not_valid(self):
        with self.assertRaises(InvalidArgument):
            self.time_source.validate_timeout_specification(
                self.time_source.timeout_specification(-1))

    def test_incorrect_units_is_not_valid(self):
        with self.assertRaises(InvalidArgument):
            self.time_source.validate_timeout_specification(
                TimeoutSpecification(1, TimeUnit.MILLIS))
