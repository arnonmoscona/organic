import unittest

from free_range.core.common.exceptions import InvalidArgument
from free_range.core.common.tests.random_mixin import RandomMixin
from free_range.core.common.time import TimeUnit, TimeoutSpecification


class TimeoutSpecificationConstructorTests(RandomMixin, unittest.TestCase):
    def setUp(self):
        self.timeout = self.random_natural()

    def test_constructor_with_good_arguments_reflects_arguments(self):
        tos = TimeoutSpecification(self.timeout, TimeUnit.MILLIS)
        self.assertEqual(self.timeout, tos.timeout)
        self.assertEqual(TimeUnit.MILLIS, tos.units)

    def test_negative_one_is_a_alid_timeout_value(self):
        TimeoutSpecification(-1)

    def test_zero_is_not_a_valid_timeout_value(self):
        with self.assertRaises(InvalidArgument):
            TimeoutSpecification(0)

    def test_one_is_a_valid_timeout_value(self):
        TimeoutSpecification(1)

    def test_millis_is_the_default_unit(self):
        tos = TimeoutSpecification(1)
        self.assertEqual(TimeUnit.MILLIS, tos.units)


class IsBlockingTests(unittest.TestCase):
    def test_magic_number_blocks(self):
        tos = TimeoutSpecification(-1)
        self.assertTrue(tos.is_blocking)

    def test_one_is_non_blocking(self):
        tos = TimeoutSpecification(1)
        self.assertFalse(tos.is_blocking)
