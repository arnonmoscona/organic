from time import sleep
import unittest
from unittest import mock

from free_range.core.common.time import TimeSource, TimeUnit, TimeoutSpecification


class UnitsTests(unittest.TestCase):
    def test_units_are_millis(self):
        self.assertEqual(TimeSource().units, TimeUnit.MILLIS)


class TimestampTests(unittest.TestCase):
    def test_timestamp_is_float(self):
        self.assertEqual(type(TimeSource().timestamp()), float)

    def test_timestamp_self_advances(self):
        source = TimeSource()
        ts1 = source.timestamp()
        sleep(0.01)
        ts2 = source.timestamp()
        self.assertGreater(ts2, ts1)

    def test_can_use_external_time_source(self):
        source = TimeSource(injected_source=lambda: 17)
        ts = source.timestamp()
        self.assertEqual(ts, 17)

    def test_timestamp_is_a_monotonous_function(self):
        external = mock.Mock()
        external_config = {'timestamp.return_value': 2}
        external.configure_mock(**external_config)
        source = TimeSource(injected_source=external.timestamp)
        ts1 = source.timestamp()
        self.assertEqual(2, ts1)

        # make time go back
        external_config['timestamp.return_value'] = 1
        external.configure_mock(**external_config)
        ts2 = source.timestamp()
        self.assertGreaterEqual(ts2, ts1)


class TimeoutSpecificationTests(unittest.TestCase):
    """
    These tests are just for the timeout_specification() factory method. There's a separate
    test suite for the TimeoutSpecification type.
    """
    def setUp(self):
        self.time_source = TimeSource()
        self.timeout_spec = self.time_source.timeout_specification(100)

    def test_timeout_specification_factory_makes_time_spec(self):
        self.assertEqual(TimeoutSpecification, type(self.timeout_spec))

    def test_timeout_specification_factory_preserves_value(self):
        self.assertEqual(100, self.timeout_spec.timeout)

    def test_timeout_specification_factory_uses_correct_units(self):
        self.assertEqual(TimeUnit.MILLIS, self.timeout_spec.units)
