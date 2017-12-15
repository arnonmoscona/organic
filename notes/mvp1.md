# MVP1 must haves

* Basic component protocol defined
    * For req/resp only
    * Message structure
    * Opinionated serialization: protobuf (3.5)
* Basic transport plugins:
    * dev (direct calls, no serialization, but via Python messages equivalent to serialized form)
    * ZMQ over TCP
* Control plane and application plane
* Component container
* Component identification
* Component === service
* ZMQ transport
    * sync req/resp over the local network
    * TCP sockets only
* discovery (hard coded: no plugins, no options, no semantic versioning, no routing)

## Programming model:
* You state what interfaces you support inside and across components by simply defining the appropriate messages as protobufs
    * May include some standard metadata
    * All messages must statically choose a client communication mode: sync or async (later maybe streaming responses, later still lazy streaming responses), later: broadcast (via ZMQ P/S capability only)

# MVP1 exclusions

* Initially no fancy guarantees. You just need a resource and provide constraints about your tolerance
    * Even earlier version with no elasticity. Just static resource allocation.
        * Elasticity is MVP, but not needed in early development
    * E.g. if capacity is not available within N ms then request more capacity
    * Or: use only local resources or local network resources
    * No leaders, no cluster-wide guarantees, no automatic sharding
* Initially no support for versioning but may support semantic versioning and allocation by version
    * Concretely: no support for versioning at all except maybe URI placeholder with no defined semantics and no effect on discovery
* Supervisor not in MVP1
* Deployment management not in MVP1
* encryption, logging, monitoring, container lifecycle hooks not in MVP1
* Transport stacking and punting not in MVP1
* Unix domain sockets, UDP, UDP multicast not in MVP1

----

# MVP2 must haves

## Basic operational facilities

* Basic component environment support (virtual env, before-start, after-shutdown, prerequisite checks)
* Basic supervisors
* Introduction of elementary plugin support for:
    * Logging
    * Tracing
    * Resource allocation
    * Local elasticity (per machine - not coordinated across the network)
    * Circuit breakers (very basic)
* Exact version matching in discovery (probably no support for semantic matching yet)
* Elementary load balancing
* Manual component orderly/forced shutdown on a single machine
* Basic Message horizon/range support
    * Hard coded
    * Configured
    * By estimated network distance
    * By hard timeout
    * With or without bounce
    * Per message only in MVP2 (not per flow, component, application)

## Debug and test facilities

* Local distributed network modeling
* Reliable distributed test support
* Network coordinated clock with coordinated time ticks and global order guarantees
* Simplest useful forms of the following:
    * Manually control network clock ticks from command line or API
    * Manually model distributed timing, race conditions, delayes
        * Control plane protocol supported delay injection deep into the flow
        * Test API to control timing injection
        * Simulation runs as fast as the system can handle the tick number coordination
            * So tests run as fast as feasible even with timeout simulation
            * Attach arbitrary monotonic timestamps to ticks via test API
            * Maybe even simulated node clock skew
    * Business flow modeling
    * Flow initiation and termination API
    * Maybe sub-flow support
    * Logging
    * Flow tracing (with message timing)
    * Simple network topology and time skew estimation


