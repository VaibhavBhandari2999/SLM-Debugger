import os.path
import shutil

failure_demo = os.path.join(os.path.dirname(__file__), "failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(pytester):
    """
    Test a function that checks for failures in a demo script. This function copies a specified demo script to a temporary directory, runs pytest on it, and verifies that the test fails as expected. The function expects the demo script to be located in the same directory as the test and uses `syspathinsert=True` to ensure the demo script is found.
    
    Parameters:
    - pytester: A fixture provided by pytest for testing pytest itself.
    
    Returns:
    - None: The function asserts that the test fails and does
    """

    target = pytester.path.joinpath(os.path.basename(failure_demo))
    shutil.copy(failure_demo, target)
    result = pytester.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
