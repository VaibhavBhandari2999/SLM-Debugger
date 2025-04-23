import pytest_twisted
from twisted.internet.task import deferLater


def sleep():
    """
    Return a deferred that will fire immediately.
    
    This function returns a `twisted.internet.defer.Deferred` object that will
    fire (with no result) after a delay of 0 seconds. It is typically used to
    ensure that asynchronous operations are properly sequenced.
    
    Parameters:
    None
    
    Returns:
    A `twisted.internet.defer.Deferred` object that will fire immediately.
    """

    import twisted.internet.reactor

    return deferLater(clock=twisted.internet.reactor, delay=0)


@pytest_twisted.inlineCallbacks
def test_inlineCallbacks():
    yield sleep()


@pytest_twisted.ensureDeferred
async def test_inlineCallbacks_async():
    await sleep()
