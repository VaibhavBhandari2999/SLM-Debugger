import pytest


@pytest.fixture("session")
def setup(request):
    """
    Setup a costly setup process for a request.
    
    This function initializes a costly setup process and yields it for use within a context. After the context is exited, the setup is finalized.
    
    Parameters:
    request (object): The request object for which the setup is being performed.
    
    Yields:
    CostlySetup: An instance of the CostlySetup class that can be used within the context.
    
    Returns:
    None: The function does not return any value, but it finalizes the setup process upon exiting the context.
    """

    setup = CostlySetup()
    yield setup
    setup.finalize()


class CostlySetup(object):
    def __init__(self):
        """
        Initialize the object with a costly setup.
        
        This method performs a time-consuming setup that simulates resource-intensive operations, such as database connections or complex calculations. It introduces a 5-second delay to mimic a real-world scenario where setup might be expensive.
        
        Key Parameters:
        - None
        
        Output:
        - None
        
        Note:
        - The setup involves a 5-second sleep, which is used to simulate a costly operation.
        - After the setup, the `timecostly` attribute is set to 1, indicating
        """

        import time

        print("performing costly setup")
        time.sleep(5)
        self.timecostly = 1

    def finalize(self):
        del self.timecostly
