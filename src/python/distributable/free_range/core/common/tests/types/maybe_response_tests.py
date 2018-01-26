import unittest

from free_range.core.common.exceptions import FreeRangeError
from free_range.core.common.response_types import MaybeResponse


class MaybeResponseMixIn(unittest.TestCase):
    def setUp(self):
        self.maybe = MaybeResponse('req-1', interaction_start_timestamp=0)


class TestResponse(MaybeResponseMixIn):
    def test_has_response(self):
        self.assertFalse(self.maybe.has_response)

    def test_response(self):
        with self.assertRaises(FreeRangeError):
            self.maybe.response


class TestError(MaybeResponseMixIn):
    def test_error(self):
        self.assertFalse(self.maybe.error)


class TestFrameworkError(MaybeResponseMixIn):
    def test_framework_error(self):
        self.assertFalse(self.maybe.framework_error)


class TestTimeout(MaybeResponseMixIn):
    def test_timeout(self):
        self.assertFalse(self.maybe.timeout)


class TestIsCompleted(MaybeResponseMixIn):
    def test_is_completed(self):
        self.assertFalse(self.maybe.is_completed)

    def test_is_completed_started(self):
        maybe = MaybeResponse('req-2', 10)
        self.assertFalse(maybe.is_completed)

    def test_is_completed_finished(self):
        # no result...
        maybe = MaybeResponse('req-2', 10, 12)
        self.assertFalse(maybe.is_completed)


class TestResponseTime(MaybeResponseMixIn):

    def test_response_time_started(self):
        maybe = MaybeResponse('req-2', 10)
        self.assertFalse(maybe.response_time_millis)

    def test_response_time_finished(self):
        # no result... not completed
        maybe = MaybeResponse('req-2', 10, 12)
        self.assertFalse(maybe.response_time_millis)


class TestRequestId(MaybeResponseMixIn):

    def test_request_id(self):
        self.assertEqual(self.maybe.request_id, 'req-1')

    def test_request_id_missing(self):
        self.assertIsNone(MaybeResponse().request_id)

    def test_request_id_non_string(self):
        self.assertEqual(MaybeResponse(1).request_id, '1')


class TestIsValid(MaybeResponseMixIn):

    def test_is_valid(self):
        self.assertTrue(self.maybe.is_valid())

    def test_is_valid_with_timing(self):
        maybe = MaybeResponse('req-2', 10, 12)
        self.assertTrue(maybe.is_valid())

    def test_is_valid_with_bad_timing(self):
        maybe = MaybeResponse('req-2', 10, 9)
        self.assertFalse(maybe.is_valid())

