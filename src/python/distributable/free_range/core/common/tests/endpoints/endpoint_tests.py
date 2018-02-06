from unittest import TestCase

from free_range.core.common.endpoints import Endpoint
from free_range.core.common.exceptions import InvalidArgumentError


class EndpointTests(TestCase):
    def test_the_root_endpoint_class_cannot_be_instantiated(self):
        with self.assertRaises(InvalidArgumentError):
            Endpoint('any string')
