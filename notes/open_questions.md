* project naming
    * organic is taken
    * brain dead is available
    * free range is available
    * leaky abstraction is available
* What represents a single machine?
    * Do you need a special node or "batteries included component" for bridging between the the set of resources on a single machine and the rest of the local network? Or does each component on a local machine just sutomatically become part of the local network?
        * Tentatively, should have a clear notion of a local machine
            * A clear local machine boundary can also serve as the distance metric (in-process / same machine / local network, remote network with measured TTL latency)
            * A clear local machine boundary can allow for use of unix domain sockets for semantic addressing, performance, and sequestering
        * I simplifies things if there's one agreed network port that is used to interrogate the resources on a local network node
        * Having a bridge component can also serve for sequestering some resources to be accessible only be the local machine
            * But a bridge node should not be a proxy node. Don't need another point of failure
* Should load balancing be a "batteries included thing" or do I just rely on something like HA-proxy?
* Should semantic versioning be an opinionated part of resource identification?
* This starts to look a lot like node from the component perspective
    - except for the cluster services.
* But components are more like actors.
    - So how different is it from Akka?
    - simpler to use?
    - different services?
* and from Celery?
    - not task oriented
    - not for deferment

