import pytest_twisted
from twisted.internet.task import deferLater


def sleep():
    """
    A function that simulates a sleep operation using Twisted's reactor. This function does not take any parameters and returns a Deferred object that will fire after a delay of 0 seconds.
    
    Returns:
    twisted.internet.defer.Deferred: A Deferred object that will fire after the specified delay.
    """

    import twisted.internet.reactor

    return deferLater(clock=twisted.internet.reactor, delay=0)


@pytest_twisted.inlineCallbacks
def test_inlineCallbacks():
    yield sleep()


@pytest_twisted.ensureDeferred
async def test_inlineCallbacks_async():
    await sleep()
