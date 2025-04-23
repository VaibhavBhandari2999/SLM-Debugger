import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test the failure of a demo function.
    
    This function runs a pytest test on a specified demo file, ensuring that the test fails as expected. It copies the demo file to the temporary directory and runs the test using pytest. The function checks if the test fails with the expected number of failures and ensures the test run does not exit successfully.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object used for running tests.
    
    Returns:
    - None: The function asserts that the test fails and
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
