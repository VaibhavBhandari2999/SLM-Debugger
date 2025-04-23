import os.path
import shutil

failure_demo = os.path.join(os.path.dirname(__file__), "failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(pytester):
    """
    Tests the function `test_failure_demo_fails_properly` to ensure it correctly identifies and reports failures in a test case. The function copies a test file `failure_demo` to a temporary directory, runs the test using `pytest`, and checks if the test fails as expected.
    
    Key Parameters:
    - `pytester`: A fixture provided by `pytest` for testing `pytest` itself.
    
    Input:
    - `failure_demo`: A test file that is expected to fail when run through `pytest`.
    """

    target = pytester.path.joinpath(os.path.basename(failure_demo))
    shutil.copy(failure_demo, target)
    result = pytester.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
