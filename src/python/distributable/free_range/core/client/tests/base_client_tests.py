from unittest import TestCase
from unittest.mock import Mock
from uuid import UUID

from free_range.core.client.base_client import BaseClient
from free_range.core.common.exceptions import InvalidArgument
from free_range.core.common.tests.random_mixin import RandomMixin
from free_range.core.common.time import TickTimeSource


class BaseClientTestMixin(TestCase):
    def setUp(self):
        self.transport = Mock()
        self.time_source = TickTimeSource().auto_advance(True)
        self.client = BaseClient(self.transport, time_source=self.time_source)


class BaseClientConstructorTests(BaseClientTestMixin):
    def test_client_indicates_theP_transport_passed_to_the_constructor(self):
        self.assertEqual(self.transport, self.client.transport)

    def test_client_rejects_none_as_transport(self):
        with self.assertRaises(InvalidArgument):
            BaseClient(None)


class GenerateCallIdTests(BaseClientTestMixin):
    def test_generate_call_id_returns_different_values_each_time_for_same_endpoint(self):
        id1 = self.client.generate_call_id('endpoint')
        id2 = self.client.generate_call_id('endpoint')
        self.assertNotEqual(id1, id2, 'call IDs must not be constant')

    def test_the_base_id_generated_is_a_uuid(self):
        self.assertEqual(UUID, type(self.client.generate_call_id('endpoint')))


class GetTimestampTests(RandomMixin, BaseClientTestMixin):
    def test_if_a_time_source_is_provided_then_it_is_used_for_the_timestamp(self):
        source = TickTimeSource()
        t = self.random_natural()
        source.advance(t)
        client = BaseClient(self.transport, time_source=source)
        t2 = client.get_timestamp()
        self.assertEqual(t, t2, 'expected to get the time sources timestamp')


class GetTimeoutSpecificationTests(BaseClientTestMixin):
    pass  # fixme: TBD implement this


class ClockForTests(BaseClientTestMixin):
    pass  # fixme: TBD implement this
