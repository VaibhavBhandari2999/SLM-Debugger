import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test function to run a pytest test file and verify that it fails as expected.
    
    This function copies a test file named 'failure_demo' to a temporary directory, runs pytest on it, and checks that the test fails with 44 failed tests. The function ensures that the sys path is properly inserted for the test to be recognized.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest Testdir object that provides utilities to create and run tests in a temporary directory.
    
    Returns:
    - None:
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
