import pytest


@pytest.fixture
def stepwise_testdir(testdir):
    """
    Generates a test directory with a specific configuration for pytest.
    
    This function creates a test directory with a custom conftest.py and test files. The conftest.py file includes options to control the behavior of tests, such as whether a test should fail based on a command-line flag. The test files include a series of tests that can be controlled to pass or fail based on these flags.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object to which the conftest
    """

    # Rather than having to modify our testfile between tests, we introduce
    # a flag for wether or not the second test should fail.
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


def test_run_without_stepwise(stepwise_testdir):
    """
    Function to run pytest with specific flags and verify the output.
    
    This function runs pytest with the following flags:
    - `-v`: Verbose mode, which provides more detailed output.
    - `--strict-markers`: Ensures that only tests marked with the specified markers are run.
    - `--fail`: Causes pytest to fail as soon as a test fails.
    
    The function takes a `stepwise_testdir` fixture, which is assumed to be a directory containing test files.
    
    The function checks the output of
    """

    result = stepwise_testdir.runpytest("-v", "--strict-markers", "--fail")

    result.stdout.fnmatch_lines(["*test_success_before_fail PASSED*"])
    result.stdout.fnmatch_lines(["*test_fail_on_flag FAILED*"])
    result.stdout.fnmatch_lines(["*test_success_after_fail PASSED*"])


def test_fail_and_continue_with_stepwise(stepwise_testdir):
    # Run the tests with a failing second test.
    result = stepwise_testdir.runpytest(
        "-v", "--strict-markers", "--stepwise", "--fail"
    )
    assert not result.stderr.str()

    stdout = result.stdout.str()
    # Make sure we stop after first failing test.
    assert "test_success_before_fail PASSED" in stdout
    assert "test_fail_on_flag FAILED" in stdout
    assert "test_success_after_fail" not in stdout

    # "Fix" the test that failed in the last run and run it again.
    result = stepwise_testdir.runpytest("-v", "--strict-markers", "--stepwise")
    assert not result.stderr.str()

    stdout = result.stdout.str()
    # Make sure the latest failing test runs and then continues.
    assert "test_success_before_fail" not in stdout
    assert "test_fail_on_flag PASSED" in stdout
    assert "test_success_after_fail PASSED" in stdout


def test_run_with_skip_option(stepwise_testdir):
    result = stepwise_testdir.runpytest(
        "-v",
        "--strict-markers",
        "--stepwise",
        "--stepwise-skip",
        "--fail",
        "--fail-last",
    )
    assert not result.stderr.str()

    stdout = result.stdout.str()
    # Make sure first fail is ignore and second fail stops the test run.
    assert "test_fail_on_flag FAILED" in stdout
    assert "test_success_after_fail PASSED" in stdout
    assert "test_fail_last_on_flag FAILED" in stdout
    assert "test_success_after_last_fail" not in stdout


def test_fail_on_errors(error_testdir):
    result = error_testdir.runpytest("-v", "--strict-markers", "--stepwise")

    assert not result.stderr.str()
    stdout = result.stdout.str()

    assert "test_error ERROR" in stdout
    assert "test_success_after_fail" not in stdout


def test_change_testfile(stepwise_testdir):
    result = stepwise_testdir.runpytest(
        "-v", "--strict-markers", "--stepwise", "--fail", "test_a.py"
    )
    assert not result.stderr.str()

    stdout = result.stdout.str()
    assert "test_fail_on_flag FAILED" in stdout

    # Make sure the second test run starts from the beginning, since the
    # test to continue from does not exist in testfile_b.
    result = stepwise_testdir.runpytest(
        "-v", "--strict-markers", "--stepwise", "test_b.py"
    )
    assert not result.stderr.str()

    stdout = result.stdout.str()
    assert "test_success PASSED" in stdout


def test_stop_on_collection_errors(broken_testdir):
    """
    Function to run pytest with specific options and collect results.
    
    This function executes pytest with the given options and returns the result.
    
    Parameters:
    broken_testdir (pytest.Testdir): A pytest Testdir fixture that provides a temporary directory for testing.
    
    Returns:
    _pytest.runner.Result: The result object containing the output and status of the pytest run.
    
    Key Options:
    -v: Verbose output.
    --strict-markers: Strictly interpret markers.
    --stepwise: Run tests stepwise
    """

    result = broken_testdir.runpytest(
        "-v",
        "--strict-markers",
        "--stepwise",
        "working_testfile.py",
        "broken_testfile.py",
    )

    stdout = result.stdout.str()
    assert "errors during collection" in stdout
