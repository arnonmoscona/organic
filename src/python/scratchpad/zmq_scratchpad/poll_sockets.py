# encoding: utf-8
#
#   Reading from multiple sockets
#   This version uses zmq.Poller()
#
#   Author: Jeremy Avnet (brainsik) <spork(dash)zmq(at)theory(dot)org>
#

import zmq

print(f'Using zmq version {zmq.zmq_version()}')
print(f'      pyzmq version {zmq.pyzmq_version()}')
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


def sync_req(message):
    print('sending sync...')
    requester.send_string(f'sync request "{message}"')

    # same process... so fake it
    print('   receiving on requester socket...')
    req = receiver.recv_string()
    receiver_behavior(req, 0, participants)

    # back home...
    response = requester.recv_string()
    print(f'    got back: {response}')


# Process messages from both sockets
# In reality should probably use lazy pirate
while True:
    should_stop = False
    try:
        # see http://pyzmq.readthedocs.io/en/latest/api/zmq.html#polling
        # polling can be done with a timeout, which can allow to check liveness when there's no
        # activity...
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

print('\nFor kicks, polling with timeout...')
socks = dict(poller.poll(1000))
# this is good for a supervisor, but also to periodically to
# maintenance when there is no activity on any socket
if not socks:
    print('    Yep, got a timeout\n')


sync_req('hello')


poller.unregister(receiver)
poller.unregister(requester)


print('Trying receive timeout...')

requester.setsockopt(zmq.RCVTIMEO, 1000)
requester.send_string('test')  # should also use socket timeout on send...
try:
    response = requester.recv_string()
except zmq.error.Again as ex:
    print(f'    got exception: {ex.__class__}/{ex.errno}: {ex.strerror}')
    print('     So can I try to receive again now (without resending)?')
    requester.setsockopt(zmq.RCVTIMEO, 0)  # 0 => return immediately, -1 => block
    try:
        response = requester.recv_string()
    except zmq.error.Again as ex:
        print(f'        got exception: {ex.__class__}/{ex.errno}: {ex.strerror}')
        print('        So yes (but cannot send)')

print('\nclosing...')
requester.close()
receiver.close()

print('Clean exit')
