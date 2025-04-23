import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Tests the `failure_demo` function to ensure it fails as expected.
    
    This function copies the `failure_demo` file to the test directory and runs pytest on it. It checks that the test fails as expected and that the exit code is non-zero.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object.
    
    Returns:
    - None: The function asserts that the test fails and the exit code is non-zero.
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
