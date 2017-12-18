# ZMQ notes

## Serialization

* pyzmq has builtin support for pickle, json, and string serialization.
  Should be easy to expose in addition to protobuf. See `morethanbindings.rst.`

## Client

* Can/should I use the zmq_scratchpad concept of "identity" as used in ROUTER sockets to more generally identify a REQ socket?
* pyzmq has a builtin tornado event loop support. Should read up and consider option.
  https://github.com/facebook/tornado. Specifically read up on tornado's `ioloop`.
  Basically allows to use callbacks instead of direct polling.
  Also look at `tornado.concurrent.Future`
* pyzmq supports async IO which converts blocking socket calls to `Future` objects.
  May want to support that at some point in the API (for async REQ/REP)
  See `eventloop.rst` in the pyzmq docs
* May want to play with coroutines or async/await for an easier API.
  See http://www.tornadoweb.org/en/stable/guide/coroutines.html
* May want to play with PyPy and stackless to get true threads instead of subprocesses

## Security

* Built-in transport level SSH is supported. Application level security not included.
* Need to understand zmq CURVE support
