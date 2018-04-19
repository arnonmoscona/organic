"""
The most basic control layer, with no fancy frills.
"""


class BasicControlLayer:
    pass  # fixme: TBD implement this

# question: is wrap() implicitly when we mark the send timestamp? Sounds wrong
# wrap(message_type, msg_id, endpoint_location, message, serializer, timeout_spec, expect_response)
# question: is unwrap implicitly when we mark the complete time? Sounds wrong
# unwrap_response(response)
# question: whwre are the events marking going over the wire?
# execute(wrapped_request)  # control delegates to exec core and wraps response
# is_expired(wrapped_request)  # should look at the outbound timeout as well as any response timeout
# log_discarded_response(wrapped_response)
# log_discarded_outbound_message(wrapped_response)
# request_id(wrapped_request)
# endpoint_location_for(wrapped_request)
# interaction_start_timestamp(wrapped_request)
# message_matches(wrapped_message, endpoint_location, request_id)
# response_matches(wrapped_response, endpoint_location, request_id)
