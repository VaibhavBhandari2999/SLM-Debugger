import os.path
import shutil

failure_demo = os.path.join(os.path.dirname(__file__), "failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(pytester):
    """
    Test the 'test_failure_demo_fails_properly' function.
    
    This function runs a test on a specified test file, ensuring that the test fails as expected. The test file is copied to a temporary location, and the function uses pytest to execute the test. The function checks for the expected number of failures and ensures the test fails correctly.
    
    Parameters:
    - pytester (Pytester): A fixture provided by pytest for testing pytest itself.
    
    Returns:
    - None: The function asserts that the test fails
    """

    target = pytester.path.joinpath(os.path.basename(failure_demo))
    shutil.copy(failure_demo, target)
    result = pytester.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
