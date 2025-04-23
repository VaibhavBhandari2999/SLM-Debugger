import py

failure_demo = py.path.local(__file__).dirpath("failure_demo.py")
pytest_plugins = ("pytester",)


def test_failure_demo_fails_properly(testdir):
    """
    Test function to run a pytest on a specific file and verify that it fails as expected.
    
    This function takes a test directory object as input and performs the following steps:
    1. Copies the `failure_demo` file to the temporary directory of the test.
    2. Copies the `failure_demo` file from the temporary directory to the target directory.
    3. Runs pytest on the target file with `syspathinsert` option enabled.
    4. Checks if the output matches the expected failure count.
    5. Assert
    """

    target = testdir.tmpdir.join(failure_demo.basename)
    failure_demo.copy(target)
    failure_demo.copy(testdir.tmpdir.join(failure_demo.basename))
    result = testdir.runpytest(target, syspathinsert=True)
    result.stdout.fnmatch_lines(["*44 failed*"])
    assert result.ret != 0
