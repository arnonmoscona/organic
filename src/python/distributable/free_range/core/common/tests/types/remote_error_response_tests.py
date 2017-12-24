import unittest

from free_range.core.common.types import RemoteErrorResponse


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

    def test_not_error_case_is_not_valid(self):
        self.assertFalse(self.no_error_data.is_valid())
