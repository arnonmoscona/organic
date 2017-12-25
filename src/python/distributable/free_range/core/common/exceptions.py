"""
Exceptions that may be raised by the framework.
"""


class FreeRangeError(Exception):
    """
    Base class for all framework exceptions. Any other type of raised exception is considered a bug.
    """
    def __init__(self, msg=None, caused_by=None, request_id=None, response=None, *args):
        super().__init__(msg, *args)
        self._caused_by = caused_by
        self._request_id = request_id
        self._response = response

    # fixme: _str__
    @property
    def caused_by(self):
        return self._caused_by

    @property
    def request_id(self):
        return self._request_id

    @property
    def response(self):
        return self._response


class ResponseTimeout(FreeRangeError):
    """
    A timeout occurred while waiting for a remote response
    """
    def __init__(self, msg=None, caused_by=None, request_id=None, response=None, *args, **kwargs):
        super().__init__(msg or 'Timeout waiting for response', caused_by, request_id, response,
                         *args, **kwargs)

    # fixme: _str__

class RemoteError(FreeRangeError):
    """
    The response from the remote party was an error response
    """
    def __init__(self, msg=None, caused_by=None, request_id=None, response=None, *args, **kwargs):
        super().__init__(msg or 'Remote response was an error', caused_by, request_id, response,
                         *args, **kwargs)

    # fixme: _str__

class FreeRangeFrameworkBug(FreeRangeError):
    """
    An internal error condition in the free-range code.
    """
    def __init__(self, msg=None, caused_by=None, request_id=None, response=None, *args, **kwargs):
        super().__init__(msg or 'Internal bug in free-range detected. Please report.', caused_by,
                         request_id, response, *args, **kwargs)

    # fixme: _str__
