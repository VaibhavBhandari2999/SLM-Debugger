import pytest
from _pytest.monkeypatch import MonkeyPatch
from _pytest.pytester import Pytester


@pytest.fixture
def stepwise_pytester(pytester: Pytester) -> Pytester:
    """
    Generates a Pytester instance for testing stepwise execution of tests.
    
    This function creates a Pytester instance with a custom conftest and test files to test stepwise execution of tests. It allows for controlling the failure of tests through command-line options.
    
    Parameters:
    pytester (Pytester): The Pytester instance to be customized.
    
    Returns:
    Pytester: The customized Pytester instance.
    
    The function sets up a conftest with options to control test failures and creates two test files,
    """

    # Rather than having to modify our testfile between tests, we introduce
    # a flag for whether or not the second test should fail.
    pytester.makeconftest(
        """
def pytest_addoption(parser):
    group = parser.getgroup('general')
    group.addoption('--fail', action='store_true', dest='fail')
    group.addoption('--fail-last', action='store_true', dest='fail_last')
"""
    )

    # Create a simple test suite.
    pytester.makepyfile(
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

    pytester.makepyfile(
        test_b="""
def test_success():
    assert 1
"""
    )

    # customize cache directory so we don't use the tox's cache directory, which makes tests in this module flaky
    pytester.makeini(
        """
        [pytest]
        cache_dir = .cache
    """
    )

    return pytester


@pytest.fixture
def error_pytester(pytester: Pytester) -> Pytester:
    pytester.makepyfile(
        test_a="""
def test_error(nonexisting_fixture):
    assert 1

def test_success_after_fail():
    assert 1
"""
    )

    return pytester


@pytest.fixture
def broken_pytester(pytester: Pytester) -> Pytester:
    """
    Generate a pytester instance with two test files.
    
    This function creates a pytester instance with two test files. The first test file, `working_testfile`, contains a properly formatted test case that should pass. The second test file, `broken_testfile`, contains invalid code and should fail.
    
    Parameters:
    pytester (Pytester): The pytester fixture used to create and manage test files.
    
    Returns:
    Pytester: The pytester instance with the specified test files.
    """

    pytester.makepyfile(
        working_testfile="def test_proper(): assert 1", broken_testfile="foobar"
    )
    return pytester


def _strip_resource_warnings(lines):
    """
    Strips unreliable ResourceWarnings from a list of lines.
    
    This function filters out lines that start with "Exception ignored in:" or "ResourceWarning" from a given list of lines. It is particularly useful for processing output where such warnings can interfere with assertions about the absence of specific error messages.
    
    Parameters:
    lines (list of str): A list of strings representing lines of text.
    
    Returns:
    list of str: A filtered list of lines with ResourceWarnings removed.
    
    Example:
    >>> _strip_resource
    """

    # Strip unreliable ResourceWarnings, so no-output assertions on stderr can work.
    # (https://github.com/pytest-dev/pytest/issues/5088)
    return [
        x
        for x in lines
        if not x.startswith(("Exception ignored in:", "ResourceWarning"))
    ]


def test_run_without_stepwise(stepwise_pytester: Pytester) -> None:
    result = stepwise_pytester.runpytest("-v", "--strict-markers", "--fail")
    result.stdout.fnmatch_lines(["*test_success_before_fail PASSED*"])
    result.stdout.fnmatch_lines(["*test_fail_on_flag FAILED*"])
    result.stdout.fnmatch_lines(["*test_success_after_fail PASSED*"])


def test_stepwise_output_summary(pytester: Pytester) -> None:
    pytester.makepyfile(
        """
        import pytest
        @pytest.mark.parametrize("expected", [True, True, True, True, False])
        def test_data(expected):
            assert expected
        """
    )
    result = pytester.runpytest("-v", "--stepwise")
    result.stdout.fnmatch_lines(["stepwise: no previously failed tests, not skipping."])
    result = pytester.runpytest("-v", "--stepwise")
    result.stdout.fnmatch_lines(
        ["stepwise: skipping 4 already passed items.", "*1 failed, 4 deselected*"]
    )


def test_fail_and_continue_with_stepwise(stepwise_pytester: Pytester) -> None:
    """
    Run tests in a stepwise manner with a failing test and continue after fixing it.
    
    This function tests the behavior of pytest when running tests in a stepwise manner with a failing test. It ensures that the test runner stops after the first failing test and continues from there after the failing test is fixed.
    
    Parameters:
    stepwise_pytester (Pytester): A fixture that provides a pytest instance for testing.
    
    Returns:
    None: The function asserts the expected behavior through assertions in the test cases.
    """

    # Run the tests with a failing second test.
    result = stepwise_pytester.runpytest(
        "-v", "--strict-markers", "--stepwise", "--fail"
    )
    assert _strip_resource_warnings(result.stderr.lines) == []

    stdout = result.stdout.str()
    # Make sure we stop after first failing test.
    assert "test_success_before_fail PASSED" in stdout
    assert "test_fail_on_flag FAILED" in stdout
    assert "test_success_after_fail" not in stdout

    # "Fix" the test that failed in the last run and run it again.
    result = stepwise_pytester.runpytest("-v", "--strict-markers", "--stepwise")
    assert _strip_resource_warnings(result.stderr.lines) == []

    stdout = result.stdout.str()
    # Make sure the latest failing test runs and then continues.
    assert "test_success_before_fail" not in stdout
    assert "test_fail_on_flag PASSED" in stdout
    assert "test_success_after_fail PASSED" in stdout


@pytest.mark.parametrize("stepwise_skip", ["--stepwise-skip", "--sw-skip"])
def test_run_with_skip_option(stepwise_pytester: Pytester, stepwise_skip: str) -> None:
    result = stepwise_pytester.runpytest(
        "-v",
        "--strict-markers",
        "--stepwise",
        stepwise_skip,
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


def test_fail_on_errors(error_pytester: Pytester) -> None:
    result = error_pytester.runpytest("-v", "--strict-markers", "--stepwise")

    assert _strip_resource_warnings(result.stderr.lines) == []
    stdout = result.stdout.str()

    assert "test_error ERROR" in stdout
    assert "test_success_after_fail" not in stdout


def test_change_testfile(stepwise_pytester: Pytester) -> None:
    """
    Tests the stepwise execution and handling of test files in pytest.
    
    This function runs pytest in stepwise mode with specific flags and test files, ensuring that the execution follows the expected sequence and handles test failures and success appropriately. It checks for the presence of specific test outcomes in the output and verifies that the stepwise execution starts from the beginning when the test file does not contain the expected test to continue from.
    
    Parameters:
    - stepwise_pytester (Pytester): A fixture that provides a pytest instance for
    """

    result = stepwise_pytester.runpytest(
        "-v", "--strict-markers", "--stepwise", "--fail", "test_a.py"
    )
    assert _strip_resource_warnings(result.stderr.lines) == []

    stdout = result.stdout.str()
    assert "test_fail_on_flag FAILED" in stdout

    # Make sure the second test run starts from the beginning, since the
    # test to continue from does not exist in testfile_b.
    result = stepwise_pytester.runpytest(
        "-v", "--strict-markers", "--stepwise", "test_b.py"
    )
    assert _strip_resource_warnings(result.stderr.lines) == []

    stdout = result.stdout.str()
    assert "test_success PASSED" in stdout


@pytest.mark.parametrize("broken_first", [True, False])
def test_stop_on_collection_errors(
    broken_pytester: Pytester, broken_first: bool
) -> None:
    """Stop during collection errors. Broken test first or broken test last
    actually surfaced a bug (#5444), so we test both situations."""
    files = ["working_testfile.py", "broken_testfile.py"]
    if broken_first:
        files.reverse()
    result = broken_pytester.runpytest("-v", "--strict-markers", "--stepwise", *files)
    result.stdout.fnmatch_lines("*error during collection*")


def test_xfail_handling(pytester: Pytester, monkeypatch: MonkeyPatch) -> None:
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
    pytester.makepyfile(contents.format(assert_value="0", strict="False"))
    result = pytester.runpytest("--sw", "-v")
    result.stdout.fnmatch_lines(
        [
            "*::test_a PASSED *",
            "*::test_b XFAIL *",
            "*::test_c PASSED *",
            "*::test_d PASSED *",
            "* 3 passed, 1 xfailed in *",
        ]
    )

    pytester.makepyfile(contents.format(assert_value="1", strict="True"))
    result = pytester.runpytest("--sw", "-v")
    result.stdout.fnmatch_lines(
        [
            "*::test_a PASSED *",
            "*::test_b FAILED *",
            "* Interrupted*",
            "* 1 failed, 1 passed in *",
        ]
    )

    pytester.makepyfile(contents.format(assert_value="0", strict="True"))
    result = pytester.runpytest("--sw", "-v")
    result.stdout.fnmatch_lines(
        [
            "*::test_b XFAIL *",
            "*::test_c PASSED *",
            "*::test_d PASSED *",
            "* 2 passed, 1 deselected, 1 xfailed in *",
        ]
    )
