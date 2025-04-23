import os.path
import shutil

failure_demo = os.path.join(os.path.dirname(__file__), "failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(pytester):
    """
    Test function to verify that a specific test file fails as expected.
    
    This function copies a test file to the current working directory and runs it using pytest. It checks if the test file fails as expected and ensures that the test failure is properly reported.
    
    Parameters:
    - pytester (Pytester): A Pytester fixture used to run pytest and manage test files.
    
    Returns:
    - None: The function asserts that the test file fails and the failure is reported correctly. It does not return any value but raises an
    """

    target = pytester.path.joinpath(os.path.basename(failure_demo))
    shutil.copy(failure_demo, target)
    result = pytester.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
