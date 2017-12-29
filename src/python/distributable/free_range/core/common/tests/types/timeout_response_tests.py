import unittest

from free_range.core.common.exceptions import FreeRangeFrameworkBug, ResponseTimeout
from free_range.core.common.types import TimeoutResponse


class TimeoutResponseMixIn(unittest.TestCase):
    def setUp(self):
        self.started = TimeoutResponse(500, 'req-1', 1)
        self.not_started = TimeoutResponse(500, 'req-1', None)
        self.no_id = TimeoutResponse(500, None, 1)
        self.bad_timing = TimeoutResponse(500, 'req-1', None)
        self.no_timeout_data = TimeoutResponse(None, 'req-1', 1)


class TestIsValid(TimeoutResponseMixIn):
    def test_started_case_is_valid(self):
        self.assertTrue(self.started.is_valid())

    def test_not_started_case_is_not_valid(self):
        self.assertFalse(self.not_started.is_valid())

    def test_no_id_case_is_not_valid(self):
        self.assertFalse(self.no_id.is_valid())

    def test_bad_timing_case_is_not_valid(self):
        self.assertFalse(self.bad_timing.is_valid())

    def test_no_timeout_case_is_not_valid(self):
        self.assertFalse(self.no_timeout_data.is_valid())


class TestError(TimeoutResponseMixIn):
    def test_started_case_has_error(self):
        self.assertEqual(self.started.error, 'timeout: 500ms')

    def test_not_started_case_raises_error(self):
        with self.assertRaises(FreeRangeFrameworkBug):
            self.not_started.error

    def test_no_id_case_raises_error(self):
        with self.assertRaises(FreeRangeFrameworkBug):
            self.no_id.error

    def test_bad_timing_case_raises_error(self):
        with self.assertRaises(FreeRangeFrameworkBug):
            self.bad_timing.error

    def test_no_timeout_data_case_raises_error(self):
        with self.assertRaises(FreeRangeFrameworkBug):
            self.no_timeout_data.error


class TestHasResponse(TimeoutResponseMixIn):
    def test_started_has_no_response(self):
        self.assertFalse(self.started.has_response)


class TestResponse(TimeoutResponseMixIn):
    def test_started_case_has_no_response(self):
        with self.assertRaises(ResponseTimeout):
            self.started.response

    def test_no_timeout_data_case_has_no_response(self):
        with self.assertRaises(FreeRangeFrameworkBug):
            self.no_timeout_data.response


class TestResponseTime(TimeoutResponseMixIn):
    def test_started_case_fails_on_response_time(self):
        with self.assertRaises(ResponseTimeout):
            self.started.response_time_millis

    def test_bad_timing_case_fails_on_response_time(self):
        with self.assertRaises(FreeRangeFrameworkBug):
            self.bad_timing.response_time_millis
