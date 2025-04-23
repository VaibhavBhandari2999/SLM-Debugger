import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test a function that runs a pytest on a specified target file. The function copies the target file and its associated test file, then executes pytest on the target file with the syspathinsert option. The function checks if the pytest output matches the expected failure count and ensures the test fails as expected.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object used for running tests.
    
    Returns:
    - None: The function does not return a value but checks the pytest output and ensures the test
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
