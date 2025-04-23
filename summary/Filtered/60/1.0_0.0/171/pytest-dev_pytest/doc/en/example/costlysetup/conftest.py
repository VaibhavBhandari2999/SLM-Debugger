import pytest


@pytest.fixture("session")
def setup(request):
    """
    Setup a costly resource for a request.
    
    This function initializes a `CostlySetup` object before the request and ensures it is properly finalized afterward.
    
    Parameters:
    request (object): The request object for which the setup is being performed.
    
    Yields:
    CostlySetup: The initialized `CostlySetup` object.
    
    Returns:
    None: This function does not return a value, but it yields the `CostlySetup` object for use within the request context.
    """

    setup = CostlySetup()
    yield setup
    setup.finalize()


class CostlySetup(object):
    def __init__(self):
        import time

        print("performing costly setup")
        time.sleep(5)
        self.timecostly = 1

    def finalize(self):
        del self.timecostly
