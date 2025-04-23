import pytest_twisted
from twisted.internet.task import deferLater


def sleep():
    """
    Return a deferred that fires immediately.
    
    This function returns a deferred that will fire immediately when called.
    The `clock` parameter is used to specify the reactor to use for scheduling
    the deferred, and the `delay` parameter is used to specify the delay before
    the deferred fires. In this case, the delay is set to 0, meaning the deferred
    will fire immediately.
    
    Parameters:
    clock (twisted.internet.interfaces.IReactorTime): The reactor to use for
    scheduling the deferred
    """

    import twisted.internet.reactor

    return deferLater(clock=twisted.internet.reactor, delay=0)


@pytest_twisted.inlineCallbacks
def test_inlineCallbacks():
    yield sleep()


@pytest_twisted.ensureDeferred
async def test_inlineCallbacks_async():
    await sleep()
