import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test function to run pytest on a specific test file and verify that it fails as expected.
    
    This function copies a test file named 'failure_demo' to the temporary directory of the test environment. It then runs pytest on the copied file, ensuring that the test fails as expected and that the failure is properly reported.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object used for running tests.
    
    Output:
    - result (pytest.Result): The result object containing the output and status of the
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
