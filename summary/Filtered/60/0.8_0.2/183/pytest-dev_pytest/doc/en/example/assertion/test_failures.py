import os.path
import shutil

failure_demo = os.path.join(os.path.dirname(__file__), "failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(pytester):
    """
    Test the 'test_failure_demo_fails_properly' function.
    
    This function tests the 'test_failure_demo_fails_properly' function, which copies a specified test file to a temporary directory, runs pytest on it, and checks if the test fails as expected.
    
    Parameters:
    - pytester (Pytester): A Pytester object used to run pytest and check the test results.
    
    Key Steps:
    1. Copy the 'failure_demo' file to a temporary directory.
    2. Run pytest on
    """

    target = pytester.path.joinpath(os.path.basename(failure_demo))
    shutil.copy(failure_demo, target)
    result = pytester.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
