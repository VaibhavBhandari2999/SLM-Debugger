import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test the failure of a demo script. This function runs a test on a specific demo script located at the target path. The script is expected to fail with 44 test failures. The function copies the demo script to the target directory and runs pytest with the specified arguments. The function asserts that the test run does not succeed (i.e., the return code is not zero).
    
    Parameters:
    - testdir (pytest.Testdir): The test directory object provided by pytest.
    
    Returns:
    - None: The
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
