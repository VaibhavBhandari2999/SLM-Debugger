import pytest


@pytest.fixture
def stepwise_testdir(testdir):
    """
    Generates a test directory with a specific configuration for pytest.
    
    This function creates a test directory with a custom configuration for pytest. It includes a conftest file to add command line options and a test suite with conditional test failures based on these options. The function also creates a separate test file for additional tests.
    
    Parameters:
    - testdir (pytest.Testdir): The pytest test directory object to which the configuration and files will be added.
    
    Returns:
    - pytest.Testdir: The modified pytest test directory object
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
    result = error_testdir.runpytest("-v", "--strict-markers", "--stepwise")

    assert not result.stderr.str()
    stdout = result.stdout.str()

    assert "test_error ERROR" in stdout
    assert "test_success_after_fail" not in stdout


def test_change_testfile(stepwise_testdir):
    """
    Run pytest in stepwise mode with specific flags and test files.
    
    This function executes pytest in stepwise mode with the given flags and test files. It ensures that the test run starts from the beginning if the test to continue from does not exist in the second test file.
    
    Parameters:
    stepwise_testdir (pytest.fixture): A fixture that provides a test directory for running pytest in stepwise mode.
    
    Returns:
    None: The function does not return anything. It prints the test results to the standard
    """

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
    result = broken_testdir.runpytest(
        "-v",
        "--strict-markers",
        "--stepwise",
        "working_testfile.py",
        "broken_testfile.py",
    )

    stdout = result.stdout.str()
    assert "errors during collection" in stdout
ise_testdir.runpytest(
        "-v", "--strict-markers", "--stepwise", "test_b.py"
    )
    assert not result.stderr.str()

    stdout = result.stdout.str()
    assert "test_success PASSED" in stdout


def test_stop_on_collection_errors(broken_testdir):
    result = broken_testdir.runpytest(
        "-v",
        "--strict-markers",
        "--stepwise",
        "working_testfile.py",
        "broken_testfile.py",
    )

    stdout = result.stdout.str()
    assert "errors during collection" in stdout
