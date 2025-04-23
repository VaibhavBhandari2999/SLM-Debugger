import pytest


@pytest.fixture("session")
def setup(request):
    """
    Setup a costly resource for a request.
    
    This function initializes a `CostlySetup` object and yields it for use during the request. After the request is processed, the `CostlySetup` object's `finalize` method is called to clean up resources.
    
    Parameters:
    request (object): The request object for which the setup is being performed.
    
    Yields:
    CostlySetup: An instance of the `CostlySetup` class that can be used during the request.
    
    Returns:
    None
    """

    setup = CostlySetup()
    yield setup
    setup.finalize()


class CostlySetup:
    def __init__(self):
        import time

        print("performing costly setup")
        time.sleep(5)
        self.timecostly = 1

    def finalize(self):
        del self.timecostly
