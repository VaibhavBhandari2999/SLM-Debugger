import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Tests the failure of a demo function. This function runs a pytest on a specified target file, ensuring that the test fails as expected. The target file is a copy of the original failure_demo file, and the test is executed with the syspathinsert flag to include the test directory in the system path.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object used to run the test.
    
    Returns:
    - None: The function asserts that the test fails with 44 failed tests
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
