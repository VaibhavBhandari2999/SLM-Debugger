import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test function to verify that a test case fails as expected.
    
    This function runs a test case located at the specified target path. The test case is expected to fail, and the function checks that the test failure is reported correctly. The test is executed with the `pytest` command, and the sys path is inserted to ensure the test can be found.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest Testdir object that provides utilities to create and run tests.
    
    The function does not return a
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
