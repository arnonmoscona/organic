# Motivations

## Happy developers

* Brain dead simple to develop a component
    * Focus on the application logic. We'll take care of the rest
    * Trivial development and debugging in a locally modeled network
    * Use your favorite tools
    * No concurrency issues to deal with (almost)
        * "almost" because there are timing issues, but we have your back for that too
    * Share-nothing architecture: don't worry about state leakage, shared mutable objects
    * Deployment environment behaves almost identically to dev/debug
* Built-in support for distributed debugging
    * Ability to locally model network, timing, race conditions
* Clear steps to distribution, protocol definitions
    * Widely used interface IDL
    * Node-like local package deployments (even independent of virtual env)
    * Components do not have to be pip packages. They're just code.
* Interoperability on business message level
    * Can always escape out of this crazy thing with little change required
    * Specifically: control plane messages are completely separate from
      the application plane, and application plane messages are *not
      forced* to use protobuf
* Very similar development process for different modes
* CI friendly

## Happy ops

* Simple deployment model
* CD friendly
* Autoscaling, elasticity out of the box in any environment
* Auto-restart for malfunctioning components
* Circuit breakers built-in
* Component startup order largely doesn't mater (ZMQ sockets take care of the magic)
* Multi-DC features, with
    * Message horizons configurable per component, app, network, named flow
    * Cross-DC flow rate limits via flow rate triggered circuit throttles
        * Local overflow option
        * Overflow drop option
        * Overflow bounce option
* Eventually automated network-wide deployment
* Eventually automated canaries, staged rollout
* Built-in support for clean structured logging
* Production tracing support
* Production per-flow or per component manual detailed debug tracing
* Support for monitoring out of the box

## Happy management

Don't paticularly care right now...

# Principles

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

