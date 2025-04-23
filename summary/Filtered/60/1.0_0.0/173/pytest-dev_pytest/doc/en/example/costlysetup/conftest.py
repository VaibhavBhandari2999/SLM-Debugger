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
        
        This method performs a time-consuming setup that simulates resource-intensive operations. It prints a message indicating the start of the setup, waits for 5 seconds to simulate the setup time, and then sets an attribute `timecostly` to 1.
        
        Parameters:
        None
        
        Returns:
        None
        
        Example:
        ```python
        obj = YourClassName()
        ```
        """

        import time

        print("performing costly setup")
        time.sleep(5)
        self.timecostly = 1

    def finalize(self):
        del self.timecostly
