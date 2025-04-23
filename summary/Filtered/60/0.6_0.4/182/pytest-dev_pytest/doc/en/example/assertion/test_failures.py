import os.path
import shutil

failure_demo = os.path.join(os.path.dirname(__file__), "failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(pytester):
    """
    Tests the failure of a specific function.
    
    This function runs a test on a copied version of a file named 'failure_demo' located in the pytester path. The test checks if the function fails as expected and matches the expected number of failures. The function uses the `pytester` fixture to run the test and expects the test to fail.
    
    Parameters:
    - pytester (Pytester): A fixture provided by pytest for testing pytest plugins.
    
    Returns:
    - None: The function asserts that the test fails
    """

    target = pytester.path.joinpath(os.path.basename(failure_demo))
    shutil.copy(failure_demo, target)
    result = pytester.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
