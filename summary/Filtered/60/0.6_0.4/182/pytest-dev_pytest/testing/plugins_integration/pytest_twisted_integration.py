import pytest_twisted
from twisted.internet.task import deferLater


def sleep():
    """
    Return a deferred that will fire after a delay of 0 seconds.
    
    This function does not take any parameters and uses the twisted.internet.reactor to create a deferred that fires immediately.
    The output is a twisted Deferred object that has fired.
    """

    import twisted.internet.reactor

    return deferLater(clock=twisted.internet.reactor, delay=0)


@pytest_twisted.inlineCallbacks
def test_inlineCallbacks():
    yield sleep()


@pytest_twisted.ensureDeferred
async def test_inlineCallbacks_async():
    await sleep()
