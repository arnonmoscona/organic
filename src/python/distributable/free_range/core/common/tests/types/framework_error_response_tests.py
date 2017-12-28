import unittest

from free_range.core.common.exceptions import FreeRangeFrameworkBug
from free_range.core.common.types import FrameworkErrorResponse


class FrameworkErrorResponseResponseMixIn(unittest.TestCase):
    def setUp(self):
        self.boom = Exception('boom')
        self.full = FrameworkErrorResponse(self.boom, 'req-1', 10, 12)
        self.no_error_data = FrameworkErrorResponse(None, 'req-1', 10, 12)
        self.bad_error_data = FrameworkErrorResponse('not an exception', 'req-1', 10, 12)
        self.no_id = FrameworkErrorResponse(self.boom, None, 10, 12)
        self.no_timing = FrameworkErrorResponse(self.boom, 'req-1')
        self.bad_timing = FrameworkErrorResponse(self.boom, 'req-1', 10, 1)


class TestIsValid(FrameworkErrorResponseResponseMixIn):
    def test_full_case_is_valid(self):
        self.assertTrue(self.full.is_valid())

    def test_bad_error_data_is_not_valid(self):
        self.assertFalse(self.bad_error_data.is_valid())

    def test_no_id_case_is_not_valid(self):
        self.assertFalse(self.no_id.is_valid())

    def test_bad_timing_case_is_not_valid(self):
        self.assertFalse(self.bad_timing.is_valid())

    def test_no_error_case_is_not_valid(self):
        self.assertFalse(self.no_error_data.is_valid())


class TestError(FrameworkErrorResponseResponseMixIn):
    def test_full_case_has_error(self):
        self.assertEqual(self.full.framework_error, self.boom)

    def test_no_id_case_has_error(self):
        self.assertEqual(self.no_id.framework_error, self.boom)

    def test_bad_timing_case_has_error(self):
        self.assertEqual(self.bad_timing.framework_error, self.boom)

    def test_no_error_data_case_has_no_error(self):
        self.assertIsNone(self.no_error_data.error)


class TestHasResponse(FrameworkErrorResponseResponseMixIn):
    def test_full_case_has_no_response(self):
        self.assertFalse(self.full.has_response)


class TestResponse(FrameworkErrorResponseResponseMixIn):
    def test_full_case_has_no_response(self):
        with self.assertRaises(FreeRangeFrameworkBug):
            self.full.response

    def test_no_error_data_case_has_no_response(self):
        with self.assertRaises(FreeRangeFrameworkBug):
            self.no_error_data.response


class TestResponseTime(FrameworkErrorResponseResponseMixIn):
    def test_full_case_reports_correct_response_time(self):
        self.assertEqual(self.full.response_time_millis, 2)

    def test_no_id_case_returns_response_time(self):
        self.assertEqual(self.no_id.response_time_millis, 2)

    def test_bad_timing_case_fails_on_response_time(self):
        with self.assertRaises(FreeRangeFrameworkBug):
            self.bad_timing.response_time_millis

