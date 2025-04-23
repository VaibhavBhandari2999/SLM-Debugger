import pytest


@pytest.fixture("session")
def setup(request):
    """
    Setup a costly resource for a request.
    
    This function sets up a costly resource for a request and ensures it is properly finalized after use.
    
    Parameters:
    request (object): The request object for which the setup is being performed.
    
    Yields:
    CostlySetup: An instance of the CostlySetup class that is set up for the request.
    
    Returns:
    None: This function does not return anything directly, but it yields a setup object that can be used within a context manager.
    
    Usage:
    """

    setup = CostlySetup()
    yield setup
    setup.finalize()


class CostlySetup(object):
    def __init__(self):
        """
        Initialize the object with a costly setup.
        
        This method performs a time-consuming setup that simulates resource-intensive operations. It prints a message indicating the start of the setup, waits for 5 seconds to simulate the setup time, and then sets an attribute `timecostly` to 1.
        
        Parameters:
        None
        
        Returns:
        None
        
        Notes:
        - The setup process is simulated to take 5 seconds.
        - The `timecostly` attribute is set to 1 after the setup is complete.
        """

        import time

        print("performing costly setup")
        time.sleep(5)
        self.timecostly = 1

    def finalize(self):
        del self.timecostly
