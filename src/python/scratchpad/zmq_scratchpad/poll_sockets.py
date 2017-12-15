# encoding: utf-8
#
#   Reading from multiple sockets
#   This version uses zmq.Poller()
#
#   Author: Jeremy Avnet (brainsik) <spork(dash)zmq(at)theory(dot)org>
#

import zmq


# Prepare our context and sockets
context = zmq.Context()

receiver = context.socket(zmq.REP)
requester = context.socket(zmq.REQ)

address = "tcp://127.0.0.1:5557"
# with REQ/REP connect and bind can be in any order
requester.connect(address)
receiver.bind(address)

# sleep(1)
iteration = 1
requester.send_string('Starting...') # must send before polling on reply

# Initialize poll set
poller = zmq.Poller()
poller.register(receiver, zmq.POLLIN)
poller.register(requester, zmq.POLLIN)


stop_message = 'enough already!'


def receiver_behavior(message, iteration, participants):
    print('Receiver got "{}"'.format(message))
    if iteration > 5:
        participants['receiver'].send_string(stop_message)
    else:
        participants['receiver'].send_string('Got it')
    return False


def requester_behavior(message, iteration, participants):
    print('Requester got reply: "{}"'.format(message))
    if message == stop_message:
        print("OK :-(")
        return True

    participants['requester'].send_string('Again!')
    return False


participants = {
    'receiver': receiver,
    'requester': requester,
}

behavior_binding = {
    receiver: receiver_behavior,
    requester: requester_behavior,
}

# Process messages from both sockets
while True:
    should_stop = False
    try:
        socks = dict(poller.poll())
    except KeyboardInterrupt:
        break

    for socket in socks:
        message = socket.recv().decode('UTF-8')
        should_stop = behavior_binding[socket](message, iteration, participants)
    if should_stop:
        break

    # sleep(1)
    iteration = iteration + 1


print('closing...')

poller.unregister(receiver)
poller.unregister(requester)
requester.close()
receiver.close()

print('Clean exit')
