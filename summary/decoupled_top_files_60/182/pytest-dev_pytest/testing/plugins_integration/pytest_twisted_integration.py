import pytest_twisted
from twisted.internet.task import deferLater


def sleep():
    """
    Return a deferred that fires immediately.
    
    This function returns a deferred that will fire immediately when called.
    It uses the twisted.internet.reactor to schedule the deferred to fire
    after a delay of 0 seconds. No parameters are required for this function.
    
    Returns:
    twisted.internet.defer.Deferred: A deferred that will fire immediately.
    """

    import twisted.internet.reactor

    return deferLater(clock=twisted.internet.reactor, delay=0)


@pytest_twisted.inlineCallbacks
def test_inlineCallbacks():
    yield sleep()


@pytest_twisted.ensureDeferred
async def test_inlineCallbacks_async():
    await sleep()
