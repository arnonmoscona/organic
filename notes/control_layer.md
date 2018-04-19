# Control Layer
* The control layer is free to pass control messages that contain no
  client messages. The main requirement for control is that they do no
  blocking io aside from the transport interface and that processing
  in-memory and very fast. No waiting of any kind allowed.
  *This is very important to enable transparent backpressure.*
* The control layer should allow a buffer of several messages in a
  single transmission. Simple RPC always uses one. But reactive streams
  of any kind can batch messages. Can also take advantage of the fact
  that from a Zmq perspective, you can make an atomic transmission.
  But you may need to break it into multiple frames...
* The transport must use the control layer even in the simplest case.
  But the transport should get the control layer reference from the
  base client. That is not there yet. Fix before proceeding.
