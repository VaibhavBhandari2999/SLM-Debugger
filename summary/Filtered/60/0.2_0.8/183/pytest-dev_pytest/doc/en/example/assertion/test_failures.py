import os.path
import shutil

failure_demo = os.path.join(os.path.dirname(__file__), "failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(pytester):
    """
    Test the 'test_failure_demo_fails_properly' function.
    
    This function runs a test on a specified target file, which is a copy of 'failure_demo'. The test ensures that the function correctly identifies and reports the number of failed tests. The function uses `pytester` to execute the test and checks if the output matches the expected failure count. The function also verifies that the test fails as expected.
    
    Parameters:
    - pytester: A fixture provided by `pytest` that allows for the
    """

    target = pytester.path.joinpath(os.path.basename(failure_demo))
    shutil.copy(failure_demo, target)
    result = pytester.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
