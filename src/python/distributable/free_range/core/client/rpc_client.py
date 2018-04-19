"""
The RPC behavior of a client, implemented over an asynchronous transport API.
This is not the simplest RPC client. A simpler one can be constructed over a blocking,
synchronous transport API.

This client is constructed with the intent of having a transport API that provides only send,
receive, and cancel operations. It would be greately simplified for a transport supporting a
blocking call operation.
"""
from free_range.core.common import exceptions
from free_range.core.common.decorators import public_interface
from free_range.core.common.exceptions import ResponseTimeout
from free_range.core.common.response_types import TimeoutResponse
from free_range.transport.types import TransportMessageType


class RpcClient:
    def __init__(self, base_client):
        self._base_client = base_client
        self._transport = self._base_client.transport  # fixme: validate RPC support

    @public_interface
    def call_sync_blocking(self, endpoint, message):
        # fixme: guard against uncaught exceptions
        call_id = self._base_client.generate_call_id(endpoint)
        self.validate_rpc_request(endpoint, message)
        serializer = self._base_client.get_serializer_for(endpoint)
        endpoint_location = self._base_client.route(endpoint, message)
        timeout_spec = self._base_client.get_timeout_specification(endpoint)
        timeout_clock = self._base_client.clock_for(timeout_spec).start()
        start_timestamp = self._base_client.get_timestamp()
        try:
            self._transport.send(TransportMessageType.RPC_REQ, call_id, endpoint_location, message,
                                 serializer, timeout_spec, expect_response=True)
        except ResponseTimeout as timeout:
            return TimeoutResponse(timeout, call_id, start_timestamp)

        # the return value is a asyncio.Future or something very similar
        # the future already had ensure_future called for it

        try:
            future_response = self._transport.receive(endpoint_location,
                                                      timeout_clock.remaining_timeout_spec(),
                                                      response_to=call_id)
            future_response.block_until_complete(timeout_clock.remaining_timeout_spec())
        except ResponseTimeout as timeout:
            self._transport.cancel(call_id)
            return TimeoutResponse(timeout, call_id, start_timestamp)

        # The result is already a MaybeResponse with the deserialized return object in it.
        response = future_response.result()  # we can call this because we blocked
        self.validate_rpc_response(response, endpoint)

        return response

    # fixme: async call (pattern on asyncio.Future)

    @public_interface
    def validate_rpc_request(self, endpoint, args):
        if not endpoint.supports_rpc():
            raise exceptions.InvalidArgumentError('Endpoint {} does not support RPC'
                                                  .format(endpoint))
        pass  # fixme: TBD implement this

    @public_interface
    def validate_rpc_response(self, endpoint, remote_endpoint):
        pass  # fixme: TBD implement this
