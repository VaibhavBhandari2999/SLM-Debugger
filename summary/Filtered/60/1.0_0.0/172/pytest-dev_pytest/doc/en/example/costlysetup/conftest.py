import pytest


@pytest.fixture("session")
def setup(request):
    """
    Setup a costly resource for a request.
    
    This function initializes a `CostlySetup` object and yields it for use within a context. After the context is exited, the `CostlySetup` object's `finalize` method is called to clean up resources.
    
    Parameters:
    request (object): The request object that needs the setup.
    
    Yields:
    CostlySetup: An instance of the `CostlySetup` class for use during the request.
    
    Returns:
    None: This function does not
    """

    setup = CostlySetup()
    yield setup
    setup.finalize()


class CostlySetup:
    def __init__(self):
        """
        Initialize the object with a costly setup.
        
        This method performs a time-consuming setup process and sets an attribute `timecostly` to 1.
        
        Key Parameters:
        None
        
        Keywords:
        None
        
        Returns:
        None
        
        Example:
        ```python
        obj = YourClass()
        ```
        """

        import time

        print("performing costly setup")
        time.sleep(5)
        self.timecostly = 1

    def finalize(self):
        del self.timecostly
