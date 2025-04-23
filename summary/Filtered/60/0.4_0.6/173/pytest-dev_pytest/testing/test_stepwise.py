import pytest


@pytest.fixture
def stepwise_testdir(testdir):
    """
    Generates a test directory with custom configuration and test files for stepwise testing.
    
    This function creates a test directory with a custom configuration file and two test files. The configuration file allows for controlling the failure of certain tests via command-line options. The test files contain a series of tests that are designed to be run in a stepwise manner, where the outcome of one test can influence the outcome of subsequent tests.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object to which the
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
    """
    Function to run pytest with specific flags and check the output.
    
    This function runs pytest with the provided test directory, using the flags `--strict-markers` and `--stepwise`. It then checks the output for errors and ensures that the test suite fails as expected when encountering an error.
    
    Parameters:
    - error_testdir (pytest.Testdir): A pytest Testdir object representing the test directory to be run.
    
    Returns:
    - result (pytest.Result): The result object containing the output and status of the
    """

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


@pytest.mark.parametrize("broken_first", [True, False])
def test_stop_on_collection_errors(broken_testdir, broken_first):
    """Stop during collection errors. Broken test first or broken test last
    actually surfaced a bug (#5444), so we test both situations."""
    files = ["working_testfile.py", "broken_testfile.py"]
    if broken_first:
        files.reverse()
    result = broken_testdir.runpytest("-v", "--strict-markers", "--stepwise", *files)
    result.stdout.fnmatch_lines("*errors during collection*")
ytest.mark.parametrize("broken_first", [True, False])
def test_stop_on_collection_errors(broken_testdir, broken_first):
    """Stop during collection errors. Broken test first or broken test last
    actually surfaced a bug (#5444), so we test both situations."""
    files = ["working_testfile.py", "broken_testfile.py"]
    if broken_first:
        files.reverse()
    result = broken_testdir.runpytest("-v", "--strict-markers", "--stepwise", *files)
    result.stdout.fnmatch_lines("*errors during collection*")
