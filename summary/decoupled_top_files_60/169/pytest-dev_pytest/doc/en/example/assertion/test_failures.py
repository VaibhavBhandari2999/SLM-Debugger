import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test function to run a pytest on a specified test file. The function copies the test file to the temporary directory and then runs pytest on it. The function checks if the test fails as expected and ensures the test result is not successful.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object.
    
    Returns:
    - None: The function does not return anything but checks the test result and ensures it fails as expected.
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
