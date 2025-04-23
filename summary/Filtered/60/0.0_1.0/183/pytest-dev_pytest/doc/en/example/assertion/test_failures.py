import os.path
import shutil

failure_demo = os.path.join(os.path.dirname(__file__), "failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(pytester):
    """
    Tests the 'test_failure_demo_fails_properly' function.
    
    This function copies a file named 'failure_demo' to a temporary directory and runs pytest on it. It checks if the test fails as expected and ensures that the test failure is properly reported.
    
    Parameters:
    - pytester (Pytester): A Pytester object to run pytest on the copied file.
    
    Returns:
    - None: The function asserts that the test failure is reported correctly and that the test run fails.
    """

    target = pytester.path.joinpath(os.path.basename(failure_demo))
    shutil.copy(failure_demo, target)
    result = pytester.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
