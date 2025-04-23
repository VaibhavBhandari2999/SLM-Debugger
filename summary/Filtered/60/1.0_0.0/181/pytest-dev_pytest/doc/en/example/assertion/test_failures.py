import os.path
import shutil

failure_demo = os.path.join(os.path.dirname(__file__), "failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test function to run pytest on a specified test file and verify that it fails as expected.
    
    This function copies a test file to the temporary directory, runs pytest on it, and checks if the test fails as expected.
    
    Parameters:
    testdir (pytest.Testdir): The pytest test directory object.
    
    Returns:
    None: The function asserts that the test fails and the exit code is non-zero.
    """

    target = testdir.tmpdir.join(os.path.basename(failure_demo))
    shutil.copy(failure_demo, target)
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
