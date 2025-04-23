import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Tests the failure of a demo function. The function runs a pytest on a specified target file, ensuring that the test fails as expected. The target file is a copy of the original failure_demo file. The function uses the `testdir` fixture to manage the test environment and ensures that the system path is properly inserted. The test is expected to fail, and the function checks for the correct failure count and non-zero exit code.
    
    Parameters:
    - testdir (pytest fixture): A pytest fixture that provides
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
