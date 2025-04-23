import os.path
import shutil

failure_demo = os.path.join(os.path.dirname(__file__), "failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(pytester):
    """
    Test the failure demonstration function.
    
    This function runs a pytest test on a specified target file, which is a copy of the `failure_demo` file. The test is expected to fail, and the function checks that the test results match the expected failure count. The function also ensures that the test run does not exit successfully.
    
    Parameters:
    - pytester (pytesttester): A pytest fixture used to run tests and manipulate the test environment.
    
    Returns:
    - None: The function does not return a value but asserts
    """

    target = pytester.path.joinpath(os.path.basename(failure_demo))
    shutil.copy(failure_demo, target)
    result = pytester.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
