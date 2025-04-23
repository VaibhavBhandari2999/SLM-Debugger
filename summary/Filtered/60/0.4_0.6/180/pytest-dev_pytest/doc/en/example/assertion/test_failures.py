import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test the failure of a demo function.
    
    This function runs a pytest on a specified target file, ensuring that the failure of the demo function is properly detected. The target file is copied from the test directory and the sys path is inserted for the test to run correctly. The function checks for the expected number of failed tests and ensures that the test run does not complete successfully.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object containing the test environment and utilities.
    
    Returns:
    - None
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
