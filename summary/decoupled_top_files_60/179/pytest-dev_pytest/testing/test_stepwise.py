import pytest


@pytest.fixture
def stepwise_testdir(testdir):
    """
    Generates a test directory with a specific configuration for pytest.
    
    This function creates a test directory with a custom configuration for pytest. It includes a conftest file that adds command line options to control the behavior of the tests. The test directory contains two test files, `test_a.py` and `test_b.py`, with a series of test functions that are conditionally run based on the command line options.
    
    Parameters:
    - testdir (pytest.Testdir): The test directory fixture provided by pytest.
    """

    # Rather than having to modify our testfile between tests, we introduce
    # a flag for whether or not the second test should fail.
    testdir.makeconftest(
        """
def pytest_addoption(parser):
    group = parser.getgroup('general')
    group.addoption('--fail', action='store_true', dest='fail')
    group.addoption('--fail-last', action='store_true', dest='fail_last')
"""
    )

    # Create a simple test suite.
    testdir.makepyfile(
        test_a="""
def test_success_before_fail():
    assert 1

def test_fail_on_flag(request):
    assert not request.config.getvalue('fail')

def test_success_after_fail():
    assert 1

def test_fail_last_on_flag(request):
    assert not request.config.getvalue('fail_last')

def test_success_after_last_fail():
    assert 1
"""
    )

    testdir.makepyfile(
        test_b="""
def test_success():
    assert 1
"""
    )

    # customize cache directory so we don't use the tox's cache directory, which makes tests in this module flaky
    testdir.makeini(
        """
        [pytest]
        cache_dir = .cache
    """
    )

    return testdir


@pytest.fixture
def error_testdir(testdir):
    """
    Generate a test directory with a test file that contains a test function that raises an error and a succeeding test function.
    
    This function creates a temporary test directory with a Python file named `test_a.py`. The file contains two test functions:
    - `test_error`: This test function attempts to use a non-existing fixture, which will raise an error.
    - `test_success_after_fail`: This test function asserts that 1 is equal to 1, which will pass successfully.
    
    Parameters:
    testdir (
    """

    testdir.makepyfile(
        test_a="""
def test_error(nonexisting_fixture):
    assert 1

def test_success_after_fail():
    assert 1
"""
    )

    return testdir


@pytest.fixture
def broken_testdir(testdir):
    testdir.makepyfile(
        working_testfile="def test_proper(): assert 1", broken_testfile="foobar"
    )
    return testdir


def _strip_resource_warnings(lines):
    # Strip unreliable ResourceWarnings, so no-output assertions on stderr can work.
    # (https://github.com/pytest-dev/pytest/issues/5088)
    return [
        x
        for x in lines
        if not x.startswith(("Exception ignored in:", "ResourceWarning"))
    ]


def test_run_without_stepwise(stepwise_testdir):
    result = stepwise_testdir.runpytest("-v", "--strict-markers", "--fail")

    result.stdout.fnmatch_lines(["*test_success_before_fail PASSED*"])
    result.stdout.fnmatch_lines(["*test_fail_on_flag FAILED*"])
    result.stdout.fnmatch_lines(["*test_success_after_fail PASSED*"])


def test_fail_and_continue_with_stepwise(stepwise_testdir):
    """
    Run pytest tests in a stepwise manner with specific flags and conditions.
    
    This function executes pytest tests using the stepwise mode with the `--strict-markers` and `--fail` flags. It simulates a scenario where a test fails and then gets fixed, and the test suite is run again to ensure the fix is effective.
    
    Parameters:
    stepwise_testdir (pytest_testdir.Testdir): A fixture that provides a test directory for running pytest tests.
    
    Returns:
    None: The function
    """

    # Run the tests with a failing second test.
    result = stepwise_testdir.runpytest(
        "-v", "--strict-markers", "--stepwise", "--fail"
    )
    assert _strip_resource_warnings(result.stderr.lines) == []

    stdout = result.stdout.str()
    # Make sure we stop after first failing test.
    assert "test_success_before_fail PASSED" in stdout
    assert "test_fail_on_flag FAILED" in stdout
    assert "test_success_after_fail" not in stdout

    # "Fix" the test that failed in the last run and run it again.
    result = stepwise_testdir.runpytest("-v", "--strict-markers", "--stepwise")
    assert _strip_resource_warnings(result.stderr.lines) == []

    stdout = result.stdout.str()
    # Make sure the latest failing test runs and then continues.
    assert "test_success_before_fail" not in stdout
    assert "test_fail_on_flag PASSED" in stdout
    assert "test_success_after_fail PASSED" in stdout


def test_run_with_skip_option(stepwise_testdir):
    """
    Run pytest with specific options to test stepwise execution and skipping.
    
    This function runs pytest with the following options:
    - `-v`: Verbose mode to print more information.
    - `--strict-markers`: Enforce strict usage of markers.
    - `--stepwise`: Enable stepwise execution.
    - `--stepwise-skip`: Skip tests that fail during stepwise execution.
    - `--fail`: Stop after the first failure.
    - `--fail-last`: Stop after the last failure.
    
    Parameters
    """

    result = stepwise_testdir.runpytest(
        "-v",
        "--strict-markers",
        "--stepwise",
        "--stepwise-skip",
        "--fail",
        "--fail-last",
    )
    assert _strip_resource_warnings(result.stderr.lines) == []

    stdout = result.stdout.str()
    # Make sure first fail is ignore and second fail stops the test run.
    assert "test_fail_on_flag FAILED" in stdout
    assert "test_success_after_fail PASSED" in stdout
    assert "test_fail_last_on_flag FAILED" in stdout
    assert "test_success_after_last_fail" not in stdout


def test_fail_on_errors(error_testdir):
    """
    Tests the behavior of pytest when encountering errors and the `--strict-markers` and `--stepwise` options.
    
    This function runs pytest with the specified options and checks the output for expected behavior. It ensures that the test marked with an error is correctly identified and that subsequent tests are not executed if the `--strict-markers` option is used.
    
    Parameters:
    - error_testdir (pytest fixture): A pytest fixture that provides a test directory with a specific setup for testing.
    
    Returns:
    - None
    """

    result = error_testdir.runpytest("-v", "--strict-markers", "--stepwise")

    assert _strip_resource_warnings(result.stderr.lines) == []
    stdout = result.stdout.str()

    assert "test_error ERROR" in stdout
    assert "test_success_after_fail" not in stdout


def test_change_testfile(stepwise_testdir):
    result = stepwise_testdir.runpytest(
        "-v", "--strict-markers", "--stepwise", "--fail", "test_a.py"
    )
    assert _strip_resource_warnings(result.stderr.lines) == []

    stdout = result.stdout.str()
    assert "test_fail_on_flag FAILED" in stdout

    # Make sure the second test run starts from the beginning, since the
    # test to continue from does not exist in testfile_b.
    result = stepwise_testdir.runpytest(
        "-v", "--strict-markers", "--stepwise", "test_b.py"
    )
    assert _strip_resource_warnings(result.stderr.lines) == []

    stdout = result.stdout.str()
    assert "test_success PASSED" in stdout


@pytest.mark.parametrize("broken_first", [True, False])
def test_stop_on_collection_errors(broken_testdir, broken_first):
    """Stop during collection errors. Broken test first or broken test last
    actually surfaced a bug (#5444), so we test both situations."""
    files = ["working_testfile.py", "broken_testfile.py"]
    if broken_first:
        files.reverse()
    result = broken_testdir.runpytest("-v", "--strict-markers", "--stepwise", *files)
    result.stdout.fnmatch_lines("*error during collection*")


def test_xfail_handling(testdir, monkeypatch):
    """Ensure normal xfail is ignored, and strict xfail interrupts the session in sw mode

    (#5547)
    """
    monkeypatch.setattr("sys.dont_write_bytecode", True)

    contents = """
        import pytest
        def test_a(): pass

        @pytest.mark.xfail(strict={strict})
        def test_b(): assert {assert_value}

        def test_c(): pass
        def test_d(): pass
    """
    testdir.makepyfile(contents.format(assert_value="0", strict="False"))
    result = testdir.runpytest("--sw", "-v")
    result.stdout.fnmatch_lines(
        [
            "*::test_a PASSED *",
            "*::test_b XFAIL *",
            "*::test_c PASSED *",
            "*::test_d PASSED *",
            "* 3 passed, 1 xfailed in *",
        ]
    )

    testdir.makepyfile(contents.format(assert_value="1", strict="True"))
    result = testdir.runpytest("--sw", "-v")
    result.stdout.fnmatch_lines(
        [
            "*::test_a PASSED *",
            "*::test_b FAILED *",
            "* Interrupted*",
            "* 1 failed, 1 passed in *",
        ]
    )

    testdir.makepyfile(contents.format(assert_value="0", strict="True"))
    result = testdir.runpytest("--sw", "-v")
    result.stdout.fnmatch_lines(
        [
            "*::test_b XFAIL *",
            "*::test_c PASSED *",
            "*::test_d PASSED *",
            "* 2 passed, 1 deselected, 1 xfailed in *",
        ]
    )
