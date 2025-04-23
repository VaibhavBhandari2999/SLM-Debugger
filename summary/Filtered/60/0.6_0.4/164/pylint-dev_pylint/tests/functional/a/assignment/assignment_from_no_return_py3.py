# pylint: disable=missing-docstring,too-few-public-methods

import asyncio


async def bla1():
    await asyncio.sleep(1)


async def bla2():
    await asyncio.sleep(2)


async def combining_coroutine1():
    await bla1()
    await bla2()


class Coro:
    async def func(self):
        future1 = bla1()
        future2 = bla2()
        await asyncio.gather(future1, future2)


async def combining_coroutine2():
    future1 = bla1()
    future2 = bla2()
    future3 = Coro().func()
    await asyncio.gather(future1, future2, future3)


def do_stuff():
    """
    do_stuff()
    
    This function runs two asynchronous coroutines, combining_coroutine1 and combining_coroutine2, using asyncio's event loop. It does not take any parameters and does not return any value.
    
    Key Points:
    - Uses asyncio's event loop to run coroutines.
    - Runs combining_coroutine1 and combining_coroutine2 sequentially.
    - No input parameters.
    - No output or return value.
    """

    loop = asyncio.get_event_loop()
    loop.run_until_complete(combining_coroutine1())
    loop.run_until_complete(combining_coroutine2())
