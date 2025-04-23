import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test a function that runs a pytest on a specified target file. The target file is expected to be a Python file that contains a test case. The function copies the target file to the test directory and runs pytest on it. The function checks if the test case fails as expected and ensures that the pytest run does not exit successfully.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object.
    
    Returns:
    - None: The function asserts that the test case fails and the pytest run does
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
