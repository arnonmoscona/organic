"""
Core types used throughout the framework
"""
from free_range.core.common.exceptions import (
    FreeRangeError, FreeRangeFrameworkBug, RemoteError, ResponseTimeout,
)


class MaybeResponse:
    """
    This is the base class of all remote response types.
    RPC pattern interactions always produce a MaybeResponse.
    Other interaction patterns may produce a MaybeResponse depending on the specific interaction
    contract.
    """

    def __init__(self, request_id=None, interaction_start_timestamp=None, received_timestamp=None):
        """
        :param request_id: the ID or the interaction ID that expected this response
        :param interaction_start_timestamp: the start time of the interaction in millis
        :param received_timestamp: the timestamp that the response was received by the control
            plane, which can be quite before it was actually returned to the application code.
        """
        self._request_id = str(request_id) if request_id else None
        self._interaction_start_timestamp = interaction_start_timestamp
        self._received_timestamp = received_timestamp

    # fixme: _str__
    @property
    def has_response(self):
        return False

    @property
    def response(self):
        """
        The response to a remote call. The remote response is never None.
        :return: returns the response if there was one available. None otherwise.
        :raises: ResponseTimeout, RemoteError, FreeRangeError. Anything else is a bug.
        """
        self.error_check()
        raise FreeRangeError('Attempt to retrieve a response from a MaybeResponse. '
                             'A response can only be obtained from a NBormalResponse.',
                             caused_by=None, request_id=self._request_id, response=self)

    def error_check(self):
        if not self.is_valid():
            raise FreeRangeFrameworkBug('Invalid MaybeResponse state', request_id=self.request_id,
                                        caused_by=None, response=self)
        if self.timeout:
            raise ResponseTimeout(caused_by=self.timeout, request_id=self.request_id, response=self)
        if self.error:
            raise RemoteError(caused_by=self.error, request_id=self.request_id, response=self)
        if not self.is_completed:
            raise FreeRangeError('Request is not complete yet', caused_by=None,
                                 request_id=self._request_id, response=self)

    @property
    def error(self):
        """
        :return: a RemoteError response if response was an error. None otherwise
        """
        return None

    @property
    def framework_error(self):
        """
        :return: a FrameworkError response if a framework bug was detected. None otherwise
        """
        return None

    @property
    def timeout(self):
        """
        :return: a Timeout if the operation timed out. Distinct from error.
        """
        return None

    @property
    def is_completed(self):
        """
        :return: True if the interaction completed. False means that no reponse was received yet,
            but also not timeout or remote error occurred.
        """
        return self.has_response or self.timeout or self.error

    @property
    def response_time_millis(self):
        """
        The difference in time between the initiation of the remote interaction and
        the time that the control plane noted te response coming back from the remote service.
        This time difference can be shorter than the the time between the interaction initiation
        and the time that the response is returned to te appllication code.
        :return: None if the interaction is incomplete or the response time in milliseconds.
        """
        if not self.is_completed:
            return None
        else:
            return self._received_timestamp - self._interaction_start_timestamp

    @property
    def request_id(self):
        return self._request_id

    def is_valid(self):
        """
        Validates that the MaybeResponse has a valid state that ay be returned to the
        application code.
        :return: True if valid else False
        """
        exclusive_conditions = [self.has_response, self.error, self.framework_error,
                                self.timeout]
        true_conditions_count = sum(map(lambda c: 1 if c else 0, exclusive_conditions))
        if true_conditions_count > 1:
            return False  # conditions must be mutually exclusive
        if self.is_completed:
            if (not self._interaction_start_timestamp
                    or not self._received_timestamp
                    or self._received_timestamp - self._interaction_start_timestamp < 0):
                return False  # A completed response must have valid response time data
        return True


class NormalResponse(MaybeResponse):
    """
    Represents a normal response from a remote interaction. Constructed by the framework.
    """
    def __init__(self, response_object,
                 interaction_start_timestamp, received_timestamp, request_id=None):
        super().__init__(request_id, interaction_start_timestamp, received_timestamp)
        self._response = response_object

    # fixme: _str__
    @property
    def response(self):
        self.error_check()
        if self._response_is_none():
            raise FreeRangeError('NormalResponse object with a None response')
        return self._response

    @property
    def has_response(self):
        return True

    def is_valid(self):
        return super().is_valid() and not self._response_is_none()

    def _response_is_none(self):
        return self._response is None


class RemoteErrorResponse(MaybeResponse):
    """
    Represents an error response with an error object as defined in the interaction contract.
    Constructed by the framework.
    """
    def __init__(self, error_object, request_id=None,
                 interaction_start_timestamp=None, received_timestamp=None):
        super().__init__(request_id, interaction_start_timestamp, received_timestamp)
        self._error = error_object

    # fixme: _str__
    @property
    def error(self):
        return self._error


class FrameworkErrorResponse(MaybeResponse):
    """
    Represents an error in the framework itself, which always indicates a framework bug.
    This may or may not have happened after a response was received from the remote service.
    Constructed by the framework.
    """
    def __init__(self, error_object, request_id=None,
                 interaction_start_timestamp=None, received_timestamp=None):
        super().__init__(request_id, interaction_start_timestamp, received_timestamp)
        self._framework_error = error_object

    # fixme: _str__
    @property
    def framework_error(self):
        return self._framework_error


class TimeoutResponse(MaybeResponse):
    """
    Represents a remote interaction timeout. All remote interactions that expect a response have a
    timeout specification, and blocaking forms of the client API never block forever. A
    TimeoutResponse is constructed by the framework when the interaction timed out before a
    normal response or error response was received.
    If a response of any kind is received after the interaction timed out, then the
    response time is recorded but the return value is discarded.
    """
    def __init__(self, timeout_object, request_id=None,
                 interaction_start_timestamp=None, received_timestamp=None):
        super().__init__(request_id, interaction_start_timestamp, received_timestamp)
        self._timeout = timeout_object

    # fixme: _str__
    @property
    def timeout(self):
        return self._timeout


class IncompleteResponse(MaybeResponse):
    """
    A typed incomplete interaction response. Constructed by the framework when checking for a
    response taht was not received nor timed out.
    """
    def __init__(self, request_id=None,
                 interaction_start_timestamp=None):
        super().__init__(request_id, interaction_start_timestamp, None)

    # fixme: _str__
