import os.path
import shutil

failure_demo = os.path.join(os.path.dirname(__file__), "failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(pytester):
    """
    Test the failure demonstration function.
    
    This function runs a pytest test on a specified target file. The target file is a copy of `failure_demo` located in the pytester's path. The test checks if the function fails as expected, matching the failure count to 44. The function also ensures that the test fails properly by verifying the exit code.
    
    Parameters:
    - pytester: The pytester fixture, which provides utilities to run and check pytest commands.
    
    Returns:
    - None: The function does
    """

    target = pytester.path.joinpath(os.path.basename(failure_demo))
    shutil.copy(failure_demo, target)
    result = pytester.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
