MVP1 Project Committed Goals
############################

* req/rep (RPC) support
    * plain objects with direct calls
    * protobuf serialized objects with in-process ZMQ REQ, REP, PAIR(?) sockets
    * protobuf serialized objects over ZMQ TCP REQ, REP sockets
    * Simplest possible incarnation is an "in-process shim" that is linear and single threaded.
      This is important as it is a core requirement derived from "brain dead simple to implement",
      meaning that a REQ/REP pattern should be replicable as simple function calls with no data
      shared other than pure-data function arguments. Code and logic can be shared.
        * This also means that from a component perspective, the difference between using the
          shim and using a split-process, ZMQ based coupler is only configuration.


Non-Goals
*********

* Performance

