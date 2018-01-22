import unittest
from unittest import mock

from free_range.core.common.exceptions import InvalidArgument
from free_range.core.common.tests.random_mixin import RandomMixin
from free_range.core.common.time import TickTimeSource, TimeUnit


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
