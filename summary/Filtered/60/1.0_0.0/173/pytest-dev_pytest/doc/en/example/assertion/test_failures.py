import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test function to verify that a test failure in a specified file is reported correctly.
    
    This function runs a test on a given file and checks if the test failure is reported properly.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest Testdir object used to run tests and check their results.
    
    The function copies the specified test file to the temporary directory, runs the tests with the temporary directory added to the system path, and checks if the test failure is reported correctly. It asserts that the test failure
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
