import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test function to verify that a test script fails as expected.
    
    This function runs a test script located at the specified target path and checks if the test fails as expected. It uses the `pytest` framework and the `testdir` fixture to execute the test.
    
    Parameters:
    - testdir (pytest fixture): A pytest fixture that provides a temporary directory for test files.
    
    The function copies the `failure_demo` test script to the temporary directory, runs the test using `pytest`, and checks if the test
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
