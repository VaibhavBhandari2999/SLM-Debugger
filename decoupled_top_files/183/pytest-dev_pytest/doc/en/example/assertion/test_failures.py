import os.path
import shutil

failure_demo = os.path.join(os.path.dirname(__file__), "failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(pytester):
    """
    Summary: This function runs a test on a specified file using pytest and checks if the test fails properly.
    
    Args:
    pytester (pytest.Pytester): A fixture that provides access to the pytest environment.
    
    Important Functions:
    - `shutil.copy`: Copies the specified file to a target location.
    - `pytester.runpytest`: Runs the pytest command on the specified file.
    - `result.stdout.fnmatch_lines`: Checks if the output matches the expected pattern.
    -
    """

    target = pytester.path.joinpath(os.path.basename(failure_demo))
    shutil.copy(failure_demo, target)
    result = pytester.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
