* Heuristic coordination message volume control
* Local machine communications is by ipc on platforms that support Unix domain sockets and top on others.
* Encryption only via a component, message and application lifecycle control plane plugin.. Components can transparently get security for their state transfer payloads.
* Logging and monitoring - also plugin with hooks.
* Container lifecycle decisions is a plugin. Also Component discovery.
* Control plane plugins are just components with a manifest that are contained in the governor. Probably need a bootstrap process as at minimum the first component loader has to be built-in, but possibly the command line can point at the loader if you're not using the built in one.
- So startup sequence is probably: locate security provider, then lookup component loader provider, then everything else.
* Zmq and direct call are just transports in a stack. A transport can punt a component down the stack
* Unix domain sockets, UDP, UDP multicast (not that they are hard in ZMQ)
* GRPC transport plugin
