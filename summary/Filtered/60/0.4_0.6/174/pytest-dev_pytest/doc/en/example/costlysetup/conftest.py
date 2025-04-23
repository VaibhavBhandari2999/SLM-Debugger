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
        
        This method performs a time-consuming setup that simulates resource-intensive operations, such as database connections or file I/O. It is designed to be called during the object's initialization to ensure that the setup is completed before any other operations are performed.
        
        Key Parameters:
        - None
        
        Keywords:
        - None
        
        Outputs:
        - None
        
        Note:
        - The method introduces a 5-second delay to simulate a costly setup process.
        - After the setup, the `timecostly
        """

        import time

        print("performing costly setup")
        time.sleep(5)
        self.timecostly = 1

    def finalize(self):
        del self.timecostly
