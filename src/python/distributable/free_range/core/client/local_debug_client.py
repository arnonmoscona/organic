"""
A simple shim client class that uses the calling thread as the only thread. It spawns no
sub-processes, and is intended for use with no remote components.
While the serialization is used as in a normal client, there is really no network transport
involved.
This clientr is primarily intended for debuging locally on a developer's machine with a debugger
that can inspect all state and without the complications that arise in a multi-process,
or remote debugging.
"""
from free_range.core.client.rpc_client import RpcClient


class LocalTransport:
    """
    A 'pass-through' local transport that mimics a network transport but does nothing, really.
    """


class LocalDebugClient(RpcClient):
    def __init__(self):
        super().__init__(LocalTransport())
