import os.path
import shutil

failure_demo = os.path.join(os.path.dirname(__file__), "failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(pytester):
    """
    Tests the failure of a demo function.
    
    This function runs a demo function located at a specified path and checks if it fails as expected. It copies the demo function to a temporary location, runs pytest on it, and verifies that the test fails as intended. The function ensures that the sys path is properly inserted for the test to run correctly.
    
    Parameters:
    - pytester (Pytester): A pytest fixture used to run tests.
    
    Returns:
    - None: The function asserts that the test fails and does not
    """

    target = pytester.path.joinpath(os.path.basename(failure_demo))
    shutil.copy(failure_demo, target)
    result = pytester.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
