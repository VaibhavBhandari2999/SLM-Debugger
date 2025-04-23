import os.path
import shutil

failure_demo = os.path.join(os.path.dirname(__file__), "failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(pytester):
    """
    Test the function 'test_failure_demo_fails_properly' to ensure it correctly runs a test on a copied file and checks for expected failure. The function copies a file named 'failure_demo' to a temporary directory, runs pytest on the copied file, and verifies that the test fails as expected. The function uses the `pytester` fixture to execute the test and checks the output for the expected number of failures. The function returns the result of the pytest run, which should indicate a non
    """

    target = pytester.path.joinpath(os.path.basename(failure_demo))
    shutil.copy(failure_demo, target)
    result = pytester.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
