import os.path
import shutil

failure_demo = os.path.join(os.path.dirname(__file__), "failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(pytester):
    """
    Test the function 'test_failure_demo_fails_properly' to ensure it correctly runs a test file that should fail, and checks for the expected failure count and non-zero exit code.
    
    Parameters:
    - pytester: A fixture provided by pytest for testing pytest itself.
    
    Key Steps:
    1. Copy the test file 'failure_demo' to a temporary location.
    2. Run pytest on the copied test file with the syspathinsert option to include the current directory in the Python path.
    3. Assert
    """

    target = pytester.path.joinpath(os.path.basename(failure_demo))
    shutil.copy(failure_demo, target)
    result = pytester.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
