import pytest


@pytest.fixture("session")
def setup(request):
    setup = CostlySetup()
    yield setup
    setup.finalize()


class CostlySetup:
    def __init__(self):
        """
        Initialize the object with a costly setup.
        
        This method performs a time-consuming setup that simulates resource-intensive operations, such as loading data or initializing a complex system. The setup is simulated by a 5-second sleep.
        
        Parameters:
        None
        
        Returns:
        None
        
        Notes:
        - The setup is simulated by a 5-second sleep.
        - After the setup, the `timecostly` attribute is set to 1, indicating that the costly setup has been performed.
        """

        import time

        print("performing costly setup")
        time.sleep(5)
        self.timecostly = 1

    def finalize(self):
        del self.timecostly
