* A single threaded application component container
* In all cases use the same thread.
  * First come first serve. No priority.
* Designed to be easily debugged locally with all or some of the components served from one local process
* Inherently distributed
* Mediated by ZMQ and protobufs (opinionated core, maybe unopinionated for components)
* Notion of local capacity
* Notion of local network capacity
* Notion of remote networks
* Automatic elasticity
    * Locally to local network to remote via gateway components
* Automatic resource discovery
* By default you just configure a local network “seed set” of IP addresses, the network expands itself from the seed
    * Seed only needed for automatic launching of new physical nodes with no manually provided seeds
    * Seed nodes are not special. They are only needed to start discovery.
    * You only need one functioning seed node to join
    * May use UDP for discovery if needed
* You can create an in-memory pseudo-network for development and debugging
    * Design first for local, in-process API without a real transport. Then have a transport SPI. Then a transport implementation. Repeat and rinse.
* In production environment each component node runs in its own process
    * A process will handle only one message at a time using an internal queue
    * Internally all messages are synchronous
    * Later may support a kind of steaming response (like an advanced streaming async, which may support lazy computation - but that may hold up an entire node capacity until the stream is done. It will require some fancy footwork
    * For each local node and network there’s configured capacity limits
    * Capacity limits can be adjusted in real time without requiring restarts
* Components can hook into the container lifecycle but being single threaded - this may not be needed. Container may provide an API for storing cross-invocation environment.

