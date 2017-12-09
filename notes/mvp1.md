* MVP1 must haves
    * dev, local, network support (the only plugins)
    * Control plane and application plane
    * Component container
    * Component identification
    * Component === service
    * ZMQ transport
        * sync req/resp over the local network
        * TCP sockets only
    * discovery (hard coded: no plugins, no options, no semantic versioning, no routing)
* Programming model:
    * You state what interfaces you support inside and across components by simply defining the appropriate messages as protobufs
        * May include some standard metadata
        * All messages must statically choose a client communication mode: sync or async (later maybe streaming responses, later still lazy streaming responses), later: broadcast (via ZMQ P/S capability only)
* Initially no fancy guarantees. You just need a resource and provide constraints about your tolerance
    * Even earlier version with no elasticity. Just static resource allocation.
        * Elasticity is MVP, but not needed in early dvelopment
    * E.g. if capacity is not available within N ms then request more capacity
    * Or: use only local resources or local network resources
    * No leaders, no cluster-wide guarantees, no automatic sharding
* Initially no support for versioning but may support semantic versioning and allocation by version
    * Concretely: no support for versioning at all except maybe URI placeholder with no defined semantics and no effect on discovery
* Governor not in MVP1
* Deployment management not in MVP1
* encryption, logging, monitoring, container lifecycle hooks not in MVP1
* Transport stacking and punting not in MVP1
* Unix domain sockets, UDP, UDP multicast not in MVP1
