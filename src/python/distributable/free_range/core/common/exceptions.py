"""
Exceptions that may be raised by the framework.
"""


class FreeRangeError(Exception):
    """
    Base class for all framework exceptions. Any other type of raised exception is considered a bug.
    """
    def __init__(self, msg=None, caused_by=None, request_id=None, **kwargs):
        super().__init__(msg)
        self._caused_by = caused_by
        self._request_id = request_id
        self._context = kwargs

    def __str__(self):
        return str(self._state_as_dict())

    def _state_as_dict(self):
        return {
            'exception': type(self),
            'message': self.args[0],
            'request_id': self.request_id,
            'caused_by': self.caused_by
        }

    @property
    def caused_by(self):
        return self._caused_by

    @property
    def request_id(self):
        return self._request_id

    @property
    def context(self):
        return self._context


# OR-4: too much duplicate code: clean up

class InvalidArgumentError(FreeRangeError):
    def __init__(self, msg=None, caused_by=None, request_id=None, **kwargs):
        super().__init__(msg, caused_by, request_id, **kwargs)

    def _state_as_dict(self):
        d = super()._state_as_dict()
        d.update({'exception': type(self)})
        return d


class InvalidStateError(FreeRangeError):
    def __init__(self, msg=None, caused_by=None, request_id=None, **kwargs):
        super().__init__(msg, caused_by, request_id, **kwargs)

    def _state_as_dict(self):
        d = super()._state_as_dict()
        d.update({'exception': type(self)})
        return d


class SerializationError(FreeRangeError):
    def __init__(self, msg=None, caused_by=None, request_id=None, **kwargs):
        super().__init__(msg, caused_by, request_id, **kwargs)

    def _state_as_dict(self):
        d = super()._state_as_dict()
        d.update({'exception': type(self)})
        return d


class DisallowedInCurrentStateError(FreeRangeError):
    def __init__(self, msg=None, caused_by=None, request_id=None, **kwargs):
        super().__init__(msg, caused_by, request_id, **kwargs)

    def _state_as_dict(self):
        d = super()._state_as_dict()
        d.update({'exception': type(self)})
        return d


class ResponseTimeout(FreeRangeError):
    """
    A timeout occurred while waiting for a remote response
    """
    def __init__(self, msg=None, caused_by=None, request_id=None, **kwargs):
        super().__init__(msg or 'Timeout waiting for response', caused_by, request_id, **kwargs)

    def _state_as_dict(self):
        state = super()._state_as_dict()
        state.update({
            'exception': type(self),
        })
        return state


class RemoteError(FreeRangeError):
    """
    The response from the remote party was an error response
    """
    def __init__(self, msg=None, caused_by=None, request_id=None, **kwargs):
        super().__init__(msg or 'Remote response was an error', caused_by, request_id, **kwargs)

    def _state_as_dict(self):
        state = super()._state_as_dict()
        state.update({
            'exception': type(self),
        })
        return state


class FreeRangeFrameworkBug(FreeRangeError):
    """
    An internal error condition in the free-range code.
    """
    def __init__(self, msg=None, caused_by=None, request_id=None, **kwargs):
        super().__init__(msg or 'Internal bug in free-range detected. Please report.', caused_by,
                         request_id, **kwargs)

    def _state_as_dict(self):
        state = super()._state_as_dict()
        state.update({
            'exception': type(self),
        })
        return state


class NotFoundError(FreeRangeError):
    """
    An error indicating that an item was not found
    """
    def __init__(self, item_reference, msg=None, caused_by=None, request_id=None, **kwargs):
        super().__init__(msg or 'Internal bug in free-range detected. Please report.', caused_by,
                         request_id, **kwargs)
        self.item_reference = item_reference

    def _state_as_dict(self):
        state = super()._state_as_dict()
        state.update({
            'exception': type(self),
            'item_reference': self.item_reference
        })
        return state
