import pytest


@pytest.fixture("session")
def setup(request):
    """
    Setup a costly setup process for a request.
    
    This function initializes a costly setup process and yields it for use within a context. After the context is exited, the setup process is finalized.
    
    Parameters:
    request (object): The request object for which the setup is being performed.
    
    Yields:
    CostlySetup: An instance of the CostlySetup class that can be used within the context.
    
    Returns:
    None: The function does not return any value, but it finalizes the setup process upon exiting the context
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
