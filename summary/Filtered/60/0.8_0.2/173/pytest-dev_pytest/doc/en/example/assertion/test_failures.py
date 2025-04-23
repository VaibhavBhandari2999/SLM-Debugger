import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test function to run a pytest test file and verify that it fails as expected.
    
    This function copies a test file named 'failure_demo' to the temporary directory of the test environment. It then runs pytest on the copied file with the syspathinsert option to ensure the test directory is included in the Python path. The function checks the output to ensure that exactly 44 tests failed and that the test run did not succeed (indicated by a non-zero return code).
    
    Parameters:
    - testdir (
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
