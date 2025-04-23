import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test function to run pytest on a specific test file and verify that it fails as expected.
    
    This function copies a test file named 'failure_demo' to the temporary directory and then runs pytest on it. The test is expected to fail, and the function checks that the failure is reported correctly.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest fixture that provides access to the temporary directory and other utilities.
    
    Returns:
    - None: The function asserts that the test fails and does not return a value
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
