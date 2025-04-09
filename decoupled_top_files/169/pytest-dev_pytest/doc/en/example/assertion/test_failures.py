import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test function to verify that the specified test file fails properly.
    
    Args:
    testdir (pytest.Testdir): The pytest Testdir object representing the temporary directory where the test files are located.
    
    Summary:
    This function copies the `failure_demo` file into the temporary directory and runs pytest on it with `syspathinsert` set to True. It then checks if the test fails as expected by verifying the presence of "44 failed" in the output and ensuring that the return code is
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
