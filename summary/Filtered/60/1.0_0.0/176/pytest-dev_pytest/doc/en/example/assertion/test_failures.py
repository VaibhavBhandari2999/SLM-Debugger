import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test function to run pytest on a specific test file and verify that it fails as expected.
    
    This function takes a test file named `failure_demo` and runs pytest on it. It ensures that the test fails with the expected number of failures and that the exit code is non-zero.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest fixture that provides a temporary directory for testing.
    
    Returns:
    - None: The function asserts that the test fails with the correct number of failures and that the exit code
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
