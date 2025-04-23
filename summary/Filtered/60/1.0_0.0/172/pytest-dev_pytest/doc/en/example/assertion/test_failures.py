import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test function to run a pytest on a specified test file. The function copies the test file to the temporary directory and runs pytest with the specified arguments. The function checks if the test fails as expected and ensures that the pytest exit code is non-zero.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object used for running tests.
    
    Returns:
    - None: The function asserts that the test fails and the pytest exit code is non-zero. It does not return any value.
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
