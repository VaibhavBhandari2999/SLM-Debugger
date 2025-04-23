import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test the failure of a demo function.
    
    This function runs a pytest on a specified target file, ensuring that the failure of the demo function is properly detected. The target file is expected to be a copy of the original failure_demo file, and the test is configured to include the syspath of the target directory.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object used to run the test.
    
    Output:
    - result (pytest.Result): The result object containing the outcome of the pytest
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
