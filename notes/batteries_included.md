# Batteries included

* integration patterns
    * RPC
        * protobuf serializers
        * HTTP response code interoperability
        * two way JSON serializer interoperability
        * browser JS client
        * Django/HTTP REST interoperability (server side, at least)
        * streaming response (?)
        * gRPC interoperability (?)
    * queue (non-persistent, small buffers)
        * rabbit interoperability (?)
        * kafka interoperability (?)
    * pub/sub (non-persistent, small buffers)
        * rabbit interoperability (?)
        * kafka interoperability (?)
    * job dispatching / apply async (?)
        * Celery interoperability (?)
* basic services
    * RPC load balancing
* simple service discovery
    * range support (more or less network distance)
    * service groups
    * network topology
* simple gossip
* encryption battery
    * symmetrical / shared secret
    * asymmetrical / key exchange (RSA, Diffie Helman?)
* full state transfer
