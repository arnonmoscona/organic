import asyncio
from asyncio.locks import Event


async def waiter(evt):
    print('  waiter: about to wait')
    print(f'    is set: {evt.is_set()}')
    await evt.wait()
    print('  waiter: acquired (released)')


async def start():
    print('starting')
    print('locking')
    evt = Event()  # an Event has multiple waiters. A Lock has exactly one
    print(f'hash(evt) = {hash(evt)}')  # can hash these so "easy" to kep rack
    print('calling waiter')
    # If we did await on the following line then we'd block forever
    asyncio.ensure_future(waiter(evt))  # creates a Task and runs it async
    await asyncio.sleep(1)
    print('unlocking')
    evt.set()


if __name__ == '__main__':
    # Here we use the asyncio event loop. Could use trio, or write our own
    loop = asyncio.get_event_loop()  # the event loop is required unless you want your own
    loop.run_until_complete(start())  # this is the simplest way
