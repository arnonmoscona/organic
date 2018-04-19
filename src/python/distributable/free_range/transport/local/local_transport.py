from collections import deque

from free_range.core.common.decorators import public_interface
from free_range.core.common.exceptions import (FreeRangeFrameworkBug,
                                               ResponseTimeout)
from free_range.core.common.response_types import (NormalResponse,
                                                   RemoteErrorResponse)
from free_range.core.common.time import TimeoutClock, TimeSource
from free_range.core.control.basic_control import BasicControlLayer
from free_range.transport.types import AbstractTransport


class LocalTransport(AbstractTransport):
    """
    A single threaded transport that translates all messages to function or method calls on the
    local stack. Primarily used for simple development debugging. Cannot reproduce complex timing
    behavior that require at least concurrency, if not parallel processing.
    """

    # fixme: document first come first serve, discarding on timeout

    @public_interface
    def __init__(self, resolver, control_layer=None, time_source=None):
        # fixme: document
        self._resolver = resolver  # this is normally the client instance
        self._control_layer = control_layer or BasicControlLayer()
        self._time_source = time_source or TimeSource()
        # fixme: ################################################################################
        # fixme: ################################################################################
        # fixme: ################# RPC NEEDS NO QUEUES!. JUST SUPPORT CALL DIRECTLY ######
        # fixme: ################################################################################
        # fixme: ################################################################################
        self._send_queue = deque()  # contains wrapped requests waiting for execution
        self._receive_queue = deque()  # contains wrapped responses for requests that were executed
        # fixme: set max queue length?
        #  fixme: control layer before send, after send, before response

    @public_interface
    def send(self, message_type, msg_id, endpoint_location, message, serializer, timeout_spec,
             expect_response=False):
        # fixme: check all arguments that cannot be None
        wrapped_message = self._control_layer.wrap(message_type, msg_id, endpoint_location,
                                                   message, serializer, timeout_spec,
                                                   expect_response)
        self._send_queue.append(wrapped_message)  # Lazy. Don't actually run until receive is called
        # eagerly execute the queue, otherwise may not ever execute
        self._execute_requests_until_response_for(endpoint_location, msg_id, TimeoutClock(
                                                  timeout_spec, self._time_source))
        # Now we return and wait for receive or cancel

    @public_interface
    def receive(self, endpoint_location, timeout_spec, response_to=None):
        # fixme: check all arguments that cannot be None
        if not self._send_queue and not self._receive_queue:
            # nothing to execute or receive, and in a single threaded implementation you will not
            # ever get anything to receive, so it makes sense to raise a timeout immediately (fail
            # fast)
            raise ResponseTimeout('No messages found to receive', request_id=response_to)

        if not response_to and not endpoint_location:
            return self._simple_receive(timeout_spec)  # fixme: what if there is None response?

        # the caller wants a response for a specific message id
        # maybe it's already received
        clock = TimeoutClock(self._time_source, timeout_spec).start()
        ready_response = self._search_receive_queue_for_response(endpoint_location, response_to,
                                                                 clock)
        if ready_response:
            return self._control_layer.unwrap_response(ready_response)

        response = self._execute_requests_until_response_for(endpoint_location, response_to,
                                                             clock)
        if response is None:
            # would get an wrapped empty response if the request was executed and
            # produced None in response
            raise ResponseTimeout('No messages found to receive. Dropped?', request_id=response_to)

        return self._control_layer.unwrap_response(response)

    def _simple_receive(self, timeout_spec):
        """
        Gets the next available messages, executes if necessary. We've not been asked for
        a specific response or endpoint - just what's available...
        :param timeout_spec: the timeout specification. Will not execute new requests beyond
            the implied timeout.
        :return: the next response message available
        """
        TimeoutClock(self._time_source, timeout_spec).start()
        if len(self._receive_queue) > 0:
            wrapped_response = self._receive_queue.popleft()
            return self._control_layer.unwrap_response(wrapped_response)
        if len(self._send_queue) == 0:
            raise ResponseTimeout('No available messages.')
        wrapped_response = self._control_layer.execute(self._send_queue.popleft())
        return self._control_layer.unwrap_response(wrapped_response)

    # <editor-fold desc="Move this entire functionality to appropriate module. Does not belong">
    def _execute(self, request):  # fixme: UNUSED!!!!!!!!
        # fixme: WRONG PLACE FOR THIS!
        # fixme: this whole function should be part of an execution module invoked by control
        if request is None:
            raise FreeRangeFrameworkBug('execute() called with no request message')
        if self._control_layer.is_expired(request):
            raise ResponseTimeout('Attempt to execute a request after its timeout elapsed.',
                                  request_id=self._control_layer.request_id(request))
        endpoint_location = self._control_layer.endpoint_location_for(request)
        message = self._control_layer.unwrap_request(request)
        handler = endpoint_location.callable()
        serializer = self._resolver.get_serializer_for(endpoint_location.get_endpoint())
        argument = serializer.deserialize(message)
        request_id = self._control_layer.request_id(request)

        try:
            response = handler(argument)
            received_timestamp = self._time_source.now()
            interaction_start_timestamp = self._control_layer.interaction_start_timestamp(request)
            response_message = NormalResponse(response, interaction_start_timestamp,
                                              received_timestamp, request_id=request_id)
        except Exception as ex:
            received_timestamp = self._time_source.now()
            interaction_start_timestamp = self._control_layer.interaction_start_timestamp(request)
            response_message = RemoteErrorResponse(ex, request_id, interaction_start_timestamp,
                                                   received_timestamp)
        return response_message  # fixme: wrap the response?

        # fixme: check if we even expect any response...
    # </editor-fold>

    def _search_receive_queue_for_response(self, endpoint_location, response_to, timeout_clock):
        found_it = None
        rejected = deque()
        while not found_it:
            if timeout_clock and timeout_clock.is_expired():
                raise ResponseTimeout('Timeout expired before finding a matching response',
                                      request_id=response_to)
            wrapped_response = self._receive_queue.popleft()
            if self._control_layer.response_matches(endpoint_location, response_to):
                found_it = wrapped_response
                break
            else:
                if not self._control_layer.is_expired(wrapped_response):
                    rejected.append(wrapped_response)
                else:
                    self._control_layer.log_discarded_response(wrapped_response)
        # now we scanned and maybe found it maybe not. We need to restore the receive queue
        self._receive_queue = rejected + self._receive_queue
        if timeout_clock and timeout_clock.is_expired():
            raise ResponseTimeout('Timeout expired before finding a matching response',
                                  request_id=response_to)
        return found_it  # if didn't find it then it's None

    def _execute_requests_until_response_for(self, endpoint_location, response_to, timeout_clock,
                                             execute_matching=True):
        while len(self._send_queue) > 0:
            if timeout_clock and timeout_clock.is_expired():
                raise ResponseTimeout('Timeout expired before finding a matching response',
                                      request_id=response_to)
            # get and execute the next one
            wrapped_message = self._send_queue.popleft()
            if self._control_layer.is_expired(wrapped_message):
                self._control_layer.log_discarded_outbound_message(wrapped_message)
                continue
            request_matches = self._control_layer.message_matches(wrapped_message,
                                                                  endpoint_location,
                                                                  response_to)
            response_matches = False
            wrapped_response = None
            if ((request_matches and execute_matching or not request_matches)
                    and not self._control_layer.is_expired(wrapped_message)):
                # fixme: log discarding expired as well as discarding non-expired
                # important: in a remote transport the following is async
                wrapped_response = self._control_layer.execute(wrapped_message)
                response_matches = wrapped_response and self._control_layer.response_matches(
                    wrapped_response, endpoint_location, response_to)
            if request_matches or response_matches:
                # timeout may have expired by now, but we have it, so we return it
                return wrapped_response and self._control_layer.unwrap_response(wrapped_response)
            else:
                self._receive_queue.append(wrapped_response)
        # If we got here without finding a match then we're in hot water => timeout
        raise ResponseTimeout('Timeout expired before finding a matching response',
                              request_id=response_to)

    @public_interface
    def cancel(self, msg_id):
        try:
            self._search_receive_queue_for_response(None, msg_id, None)
            self._execute_requests_until_response_for(None, msg_id, None, False)
        except ResponseTimeout:
            pass  # can just ignore in this case

    @public_interface
    def send_response_for(self, request, response):
        pass  # fixme: TBD implement this
