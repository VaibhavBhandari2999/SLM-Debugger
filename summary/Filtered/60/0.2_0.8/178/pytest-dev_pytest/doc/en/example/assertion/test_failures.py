import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test function to run pytest on a specified test file and verify that it fails as expected.
    
    This function copies a test file named 'failure_demo' to the temporary directory and runs pytest on it. It checks if the test fails as expected and ensures that the exit status of pytest is non-zero.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object used to run the tests.
    
    Returns:
    - None: The function asserts that the test fails and the exit status is non-zero.
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
