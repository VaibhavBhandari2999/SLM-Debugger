import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test function to run pytest on a specific test file and verify that it fails as expected.
    
    This function copies a test file named 'failure_demo' to the temporary directory and runs pytest on it. It checks that the test fails with 44 failed tests and ensures that the test run does not exit successfully.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest Testdir object used to run tests in the temporary directory.
    
    Returns:
    - None: The function asserts that the test run did not
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
