import os.path
import shutil

failure_demo = os.path.join(os.path.dirname(__file__), "failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(pytester):
    """
    Test the function 'test_failure_demo_fails_properly' to ensure it correctly runs a test on a copied file and validates the expected failure count and non-zero exit status.
    
    Parameters:
    - pytester (Pytester): A fixture provided by the `pytester` plugin, used for running and testing pytest itself.
    
    The function copies a file named 'failure_demo' to a temporary directory, runs pytest on the copied file with the `syspathinsert` option, and checks that the test fails
    """

    target = pytester.path.joinpath(os.path.basename(failure_demo))
    shutil.copy(failure_demo, target)
    result = pytester.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
