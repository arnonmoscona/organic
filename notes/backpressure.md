# Backpressure

* Backpressure should be in the reactive sense: The receiver tells the
  sender how many messages they are ready to receive, then the sender
  may send up to the outstanding demand and no more. So in RPC, the
  receiver is the server for the request, and the client for the
  response, although we might relax it and say that if an RPC request
  is sent, then it means that the client is ready for a response. At
  least for simple RPC. Streaming RPC is different.

* When I start queues, p/s, dreaming rpc responses, use something
  similar to reactive streams. Backpressure. Receiver sets the number of
  messages they are willing to accept. This should become an option in
  rpc as well, where the server tells clients when they are ready for a
  new request. This should be a control layer negotiation that is
  transparent to the client.

* Transparent backpressure requires passing control messages without a
  client message: pure control, no payload.
