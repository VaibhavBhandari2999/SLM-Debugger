import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Tests a function that runs a pytest on a specified target file. The target file is expected to be a Python file that contains a test case which is expected to fail. The function copies the target file to the test directory and runs pytest with the specified target. It then checks if the pytest output matches the expected failure count and ensures that the pytest run did not succeed.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object which provides methods to run pytest and check its output.
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
