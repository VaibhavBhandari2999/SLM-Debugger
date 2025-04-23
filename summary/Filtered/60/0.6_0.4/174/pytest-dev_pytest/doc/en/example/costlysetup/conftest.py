import pytest


@pytest.fixture("session")
def setup(request):
    """
    Setup a costly setup process.
    
    This function initializes a costly setup process and yields the setup object for use. After the setup is no longer needed, it is finalized.
    
    Parameters:
    request (object): The request object that triggers the setup process.
    
    Yields:
    CostlySetup: An instance of the CostlySetup class that can be used for setup tasks.
    
    Returns:
    None: This function does not return any value. It yields the setup object and finalizes it after use.
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
