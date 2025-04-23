import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test the failure of a demo script. This function runs a test on a specified demo script located at the target path. The test ensures that the script fails as expected, indicating that the failure is handled correctly. The function copies the demo script to the target directory and runs the test using pytest with the syspathinsert option. The function checks for the expected failure count and ensures the test fails as intended.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object used to run the
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
