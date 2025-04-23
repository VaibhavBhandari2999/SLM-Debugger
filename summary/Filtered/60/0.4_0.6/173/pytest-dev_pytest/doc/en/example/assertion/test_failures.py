import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Tests the failure of a demo script. This function runs a specific demo script located at the target path and checks for the expected number of failures. It ensures that the test fails as expected, indicating that the demo script is functioning correctly.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object used to run the tests.
    
    Returns:
    - None: The function asserts that the test fails with the expected number of failures and does not return a value if the test passes unexpectedly.
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
