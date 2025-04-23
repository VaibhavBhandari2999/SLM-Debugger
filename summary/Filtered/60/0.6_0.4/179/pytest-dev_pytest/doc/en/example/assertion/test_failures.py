import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Tests the failure of a demo function.
    
    This function runs a test on a demo function that is expected to fail. It copies the demo function to a temporary directory, runs the test using pytest, and checks that the test fails as expected.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object used to run the test.
    
    Output:
    - The function checks that the test fails with 44 failed tests and ensures that the test exit status is not zero.
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
