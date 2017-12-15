import time

import zmq

port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://*:%s" % port)  # Can safely recycle server, but not client

while True:
    socket.send_string("Server message to client3")
    msg = socket.recv().decode('UTF-8')
    print(msg)
    time.sleep(1)
