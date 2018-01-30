import unittest

from free_range.core.common.exceptions import (
    FreeRangeFrameworkBug, RemoteError,
)
from free_range.core.common.response_types import RemoteErrorResponse


class RemoteErrorResponseMixIn(unittest.TestCase):
    def setUp(self):
        self.full = RemoteErrorResponse('error obj1', 'req-1', 1, 2)
        self.started = RemoteErrorResponse('error obj1', 'req-1', 1, None)
        self.not_started = RemoteErrorResponse('error obj1', 'req-1', None, None)
        self.no_id = RemoteErrorResponse('error obj1', None, 1, 2)
        self.bad_timing = RemoteErrorResponse('error obj1', 'req-1', 10, 0)
        self.no_error_data = RemoteErrorResponse(None, 'req-1', 1, 2)


class TestIsValid(RemoteErrorResponseMixIn):
    def test_full_case_is_valid(self):
        self.assertTrue(self.full.is_valid())

    def test_started_case_is_not_valid(self):
        self.assertFalse(self.started.is_valid())

    def test_not_started_case_is_not_valid(self):
        self.assertFalse(self.not_started.is_valid())

    def test_no_id_case_is_not_valid(self):
        self.assertFalse(self.no_id.is_valid())

    def test_bad_timing_case_is_not_valid(self):
        self.assertFalse(self.bad_timing.is_valid())

    def test_no_error_case_is_not_valid(self):
        self.assertFalse(self.no_error_data.is_valid())


class TestError(RemoteErrorResponseMixIn):
    def test_full_case_has_error(self):
        self.assertEqual(self.full.error, 'error obj1')

    def test_started_case_has_error(self):
        self.assertEqual(self.started.error, 'error obj1')

    def test_not_started_case_has_error(self):
        self.assertEqual(self.not_started.error, 'error obj1')

    def test_no_id_case_has_error(self):
        self.assertEqual(self.no_id.error, 'error obj1')

    def test_bad_timing_case_has_error(self):
        self.assertEqual(self.bad_timing.error, 'error obj1')

    def test_no_error_data_case_has_no_error(self):
        self.assertIsNone(self.no_error_data.error)


class TestHasResponse(RemoteErrorResponseMixIn):
    def test_full_case_has_no_response(self):
        self.assertFalse(self.full.has_response)


class TestResponse(RemoteErrorResponseMixIn):
    def test_full_case_has_no_response(self):
        with self.assertRaises(RemoteError):
            self.full.response

    def test_no_error_data_case_has_no_response(self):
        with self.assertRaises(FreeRangeFrameworkBug):
            self.no_error_data.response


class TestResponseTime(RemoteErrorResponseMixIn):
    def test_full_case_reports_correct_response_time(self):
        self.assertEqual(self.full.response_time_millis, 1)

    def test_started_case_fails_on_response_time(self):
        with self.assertRaises(FreeRangeFrameworkBug):
            self.started.response_time_millis

    def test_not_started_case_fails_on_response_time(self):
        with self.assertRaises(FreeRangeFrameworkBug):
            self.not_started.response_time_millis

    def test_no_id_case_returns_response_time(self):
        self.assertEqual(self.no_id.response_time_millis, 1)

    def test_bad_timing_case_fails_on_response_time(self):
        with self.assertRaises(FreeRangeFrameworkBug):
            self.bad_timing.response_time_millis
