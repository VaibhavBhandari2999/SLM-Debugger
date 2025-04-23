import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test function to verify that a test script fails as expected.
    
    This function runs a test script located at the specified target path and checks if it fails as expected. The test script is copied to the temporary directory of the test environment. The function then executes the test using pytest with the specified target and ensures that the test fails with the expected number of failures. If the test does not fail as expected, the function will return a non-zero exit code.
    
    Parameters:
    testdir (pytest.Testdir):
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
