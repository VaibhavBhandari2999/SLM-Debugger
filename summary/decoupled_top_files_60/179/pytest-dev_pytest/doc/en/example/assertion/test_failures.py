import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test function to verify that a test script fails as expected.
    
    This function runs a test script located at the specified target path and checks if it fails as expected. The test script is copied to the temporary directory and run using pytest. The function asserts that the test script fails and that the exit code is non-zero.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object used to run the test.
    
    Returns:
    - None: The function asserts the expected behavior and does not return a
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
