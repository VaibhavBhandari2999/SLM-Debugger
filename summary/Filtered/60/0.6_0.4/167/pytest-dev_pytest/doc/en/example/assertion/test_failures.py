import os.path
import shutil

failure_demo = os.path.join(os.path.dirname(__file__), "failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(pytester):
    """
    Test the function 'test_failure_demo_fails_properly' to ensure it correctly runs a test script, checks for failures, and returns a non-zero exit status.
    
    Parameters:
    - pytester: A fixture provided by the `pytester` module, used to run pytest tests and interact with the test environment.
    
    The function copies a test script named 'failure_demo' to a temporary location, runs the test using pytest, and verifies that:
    - The test script fails as expected.
    - The output
    """

    target = pytester.path.joinpath(os.path.basename(failure_demo))
    shutil.copy(failure_demo, target)
    result = pytester.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
