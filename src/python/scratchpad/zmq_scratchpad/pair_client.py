import time

import zmq

port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://localhost:%s" % port)  # Can safely recycle server, but not client

while True:
    msg = socket.recv().decode('UTF-8')
    print(msg)
    socket.send_string("client message to server1")
    # This is an exchange. Blocks until server message received. No bufferingg
    socket.send_string("client message to server2")
    time.sleep(1)
