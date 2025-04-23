import os.path
import shutil

failure_demo = os.path.join(os.path.dirname(__file__), "failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(pytester):
    """
    Tests the `test_failure_demo_fails_properly` function.
    
    This function copies a test file `failure_demo` to a temporary directory, runs pytest on the copied file with `syspathinsert` option, and checks if the test fails as expected. The function verifies that the test output contains the expected failure count and that the test run does not succeed.
    
    Parameters:
    - pytester (Pytester): A Pytester object used to run pytest and check the test results.
    
    Returns:
    - None
    """

    target = pytester.path.joinpath(os.path.basename(failure_demo))
    shutil.copy(failure_demo, target)
    result = pytester.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
