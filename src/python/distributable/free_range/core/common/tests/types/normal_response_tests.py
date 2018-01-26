import unittest

from free_range.core.common.exceptions import FreeRangeFrameworkBug
from free_range.core.common.response_types import NormalResponse


class NormalResponseMixIn(unittest.TestCase):
    def setUp(self):
        self.maybe = NormalResponse('response', 10, 11, request_id='req-1')


class TestResponse(NormalResponseMixIn):
    def test_response(self):
        self.assertEqual(self.maybe.response, 'response')

    def test_response_with_no_response(self):
        self.maybe = NormalResponse(None, 10, 11, request_id='req-1')
        with self.assertRaises(FreeRangeFrameworkBug):
            self.maybe.response

    def test_response_with_bad_timing_data(self):
        self.maybe = NormalResponse(None, 10, 9, request_id='req-1')
        with self.assertRaises(FreeRangeFrameworkBug):
            self.maybe.response


class TestHasResponse(NormalResponseMixIn):
    def test_has_response(self):
        self.assertTrue(self.maybe.has_response)


class TestIsValid(NormalResponseMixIn):
    def test_is_valid(self):
        self.assertTrue(self.maybe.is_valid())

    def test_is_valid_with_no_response(self):
        self.maybe = NormalResponse(None, 10, 11, request_id='req-1')
        self.assertFalse(self.maybe.is_valid())

    def test_is_valid_with_bad_timing_data(self):
        self.maybe = NormalResponse('response', 10, 9, request_id='req-1')
        self.assertFalse(self.maybe.is_valid())


class TestCompleted(NormalResponseMixIn):
    def test_is_complete(self):
        self.assertTrue(self.maybe.is_completed)

    def test_is_complete_with_no_receive_timestamp(self):
        self.maybe = NormalResponse('response', 10, None, request_id='req-1')
        with self.assertRaises(FreeRangeFrameworkBug):
            self.maybe.is_completed

    def test_is_complete_with_no_start_timestamp(self):
        self.maybe = NormalResponse('response', None, 1, request_id='req-1')
        with self.assertRaises(FreeRangeFrameworkBug):
            self.maybe.is_completed

