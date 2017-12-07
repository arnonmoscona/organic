Basic idea

* A single threaded application component container
* Designed to be easily debugged locally with all or some of the components served from one local process
* Inherently distributed
* Mediated by ZMQ and protobufs (opinionated)
* Notion of local capacity
* Notion of local network capacity
* Notion of remote networks
* Automatic elasticity
    * Locally to local network to remote via gateway components
* Automatic resource discovery
* Heuristic coordination message volume control
* Local processes under a governor
* By default you just configure a local network “seed set” of IP addresses, the network expands itself from the seed
    * Seed only needed for automatic launching of new physical nodes with no manually provided seeds
    * May use UDP for discovery if needed
* Programming model:
    * You state what interfaces you support inside and across components by simply defining the appropriate messages as protobufs
        * May include some standard metadata
        * All messages must statically choose a client communication mode: sync or async (later maybe streaming responses, later still lazy streaming responses), later: broadcast (via ZMQ P/S capability only)
    * You can create an in-memory pseudo-network for development and debugging
    * In production environment each component node runs in its own process
        * A process will handle only one message at a time using an internal queue
        * Internally all messages are synchronous
        * Later may support a kind of steaming response (like an advanced streaming async, which may support lazy computation - but that may hold up an entire node capacity until the stream is done. It will require some fancy footwork
        * For each local node and network there’s configured capacity limits
        * Capacity limits can be adjusted in real time without requiring restarts
* Initially no fancy guarantees. You just need a resource and provide constraints about your tolerance
    * E.g. if capacity is not available within N ms then request more capacity
    * Or: use only local resources or local network resources
    * No leaders, no cluster-wide guarantees, no automatic sharding
* Initially no support for versioning but may support semantic versioning and allocation by version

Other notes

* Zmq socket -> uwrap message -> if control plane then route to appropriate controller object.
* If application plane then route body to the appropriate component.
* Governor may spawn new child component containers up to a limit. By default the limit is twice the processor count.
* Govvernirs may order idle containers to shut down.
* Components can hook into the container lifecycle but being single threaded - this may not be needed. Container may provide an API for storing cross-invocation environment.
* In all cases use the same thread.
  * First come first serve. No priority.
* Zmq may drop messages, blocking new ones if socket buffer full.
* Governor detects zombies by pinging on control plane and timing out on pongs in single threaded control loop.
* Governors are invisible to the component network.
* Governor may be extended with strategy plugins:
- zombie detection response
- ‎logging plugin
* One governor per local machine is the norm, but not enforced.
* Local machine communications is by ipc on platforms that support Unix domain sockets and top on others.
* Governors do not participate in discovery and are not discoverable.
* This starts to look a lot like node from the component perspective, except for the cluster services. But components are more like actors.
* Component code is discovered by path. Components sub directories that are python packages first, and then python path.
* Components may need to provide a duck typed manifest class.
* Governors do not need to be restarted when components are added, removed, or redeployed.
* Instead they periodically scan the components sub directory to detect changes.
* May need a deployment lock file or governor components shutdown messages to prevent spawning while deploying and to cleanly shut down running components before deployment.
* Maybe allow governor process to be recycled without killing children.
* Built in support for full state transfer
* Encryption only via a component, message and application lifecycle control plane plugin.. Components can transparently get security for their state transfer payloads.
* Logging and monitoring - also plugin with hooks.
* Container lifecycle decisions is a plugin. Also Component discovery.
* Control plane plugins are just components with a manifest that are contained in the governor. Probably need a bootstrap process as at minimum the first component loader has to be built-in, but possibly the command line can point at the loader if you're not using the built in one.
* So startup sequence is probably: locate security provider, then lookup component loader provider, then everything else.
* How is this difference than Celery? How is it different than Akka?
* Clients don't have to be containers. A client library can do cluster discovery and interrogation.
* Req/resp is mainly for clients.
* Messages have value, error, meta, pass through state, control headers, from, to, mode
* Zmq and direct call are just transports in a stack. A transport can punt a component down the stack
* MVP: sync req/resp over the local network with node discovery. No governors. Hard coded component discovery. No plugins other than transport.
