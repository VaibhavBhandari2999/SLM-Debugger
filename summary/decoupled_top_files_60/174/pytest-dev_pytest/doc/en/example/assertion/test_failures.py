import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test function to verify that a test failure in a specified file is reported correctly.
    
    This function runs a test on a specified file and checks if the test failure is reported properly. The test file is copied to the temporary directory and then run using pytest. The function expects the test to fail and verifies that the failure is reported with the correct number of failed tests.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object which provides utilities to run tests.
    
    The function does not return any
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
