import pytest


@pytest.fixture(params=["--setup-only", "--setup-plan", "--setup-show"], scope="module")
def mode(request):
    return request.param


def test_show_only_active_fixtures(testdir, mode):
    p = testdir.makepyfile(
        '''
        import pytest
        @pytest.fixture
        def _arg0():
            """hidden arg0 fixture"""
        @pytest.fixture
        def arg1():
            """arg1 docstring"""
        def test_arg1(arg1):
            pass
    '''
    )

    result = testdir.runpytest(mode, p)
    assert result.ret == 0

    result.stdout.fnmatch_lines(
        ["*SETUP    F arg1*", "*test_arg1 (fixtures used: arg1)*", "*TEARDOWN F arg1*"]
    )
    assert "_arg0" not in result.stdout.str()


def test_show_different_scopes(testdir, mode):
    """
    Tests the behavior of fixtures with different scopes in pytest. The function creates a test file with two fixtures: one with a function scope and one with a session scope. It then runs pytest on this test file with a specified mode and checks that the setup and teardown of the fixtures occur in the correct order.
    
    Key Parameters:
    - testdir: The pytest test directory object used to create and run tests.
    - mode: The mode in which pytest is run.
    
    Input:
    - A test file is created with
    """

    p = testdir.makepyfile(
        '''
        import pytest
        @pytest.fixture
        def arg_function():
            """function scoped fixture"""
        @pytest.fixture(scope='session')
        def arg_session():
            """session scoped fixture"""
        def test_arg1(arg_session, arg_function):
            pass
    '''
    )

    result = testdir.runpytest(mode, p)
    assert result.ret == 0

    result.stdout.fnmatch_lines(
        [
            "SETUP    S arg_session*",
            "*SETUP    F arg_function*",
            "*test_arg1 (fixtures used: arg_function, arg_session)*",
            "*TEARDOWN F arg_function*",
            "TEARDOWN S arg_session*",
        ]
    )


def test_show_nested_fixtures(testdir, mode):
    testdir.makeconftest(
        '''
        import pytest
        @pytest.fixture(scope='session')
        def arg_same():
            """session scoped fixture"""
        '''
    )
    p = testdir.makepyfile(
        '''
        import pytest
        @pytest.fixture(scope='function')
        def arg_same(arg_same):
            """function scoped fixture"""
        def test_arg1(arg_same):
            pass
    '''
    )

    result = testdir.runpytest(mode, p)
    assert result.ret == 0

    result.stdout.fnmatch_lines(
        [
            "SETUP    S arg_same*",
            "*SETUP    F arg_same (fixtures used: arg_same)*",
            "*test_arg1 (fixtures used: arg_same)*",
            "*TEARDOWN F arg_same*",
            "TEARDOWN S arg_same*",
        ]
    )


def test_show_fixtures_with_autouse(testdir, mode):
    p = testdir.makepyfile(
        '''
        import pytest
        @pytest.fixture
        def arg_function():
            """function scoped fixture"""
        @pytest.fixture(scope='session', autouse=True)
        def arg_session():
            """session scoped fixture"""
        def test_arg1(arg_function):
            pass
    '''
    )

    result = testdir.runpytest(mode, p)
    assert result.ret == 0

    result.stdout.fnmatch_lines(
        [
            "SETUP    S arg_session*",
            "*SETUP    F arg_function*",
            "*test_arg1 (fixtures used: arg_function, arg_session)*",
        ]
    )


def test_show_fixtures_with_parameters(testdir, mode):
    """
    This function tests the display of fixtures with parameters in a pytest environment. It sets up a session-scoped fixture with multiple parameters and a function-scoped fixture that depends on the session-scoped fixture. The function runs a test that uses the function-scoped fixture. The test is executed twice, once for each parameter of the session-scoped fixture, ensuring that the fixtures are properly set up and torn down for each parameter.
    
    Parameters:
    - testdir: A pytest fixture that provides a temporary test directory
    """

    testdir.makeconftest(
        '''
        import pytest
        @pytest.fixture(scope='session', params=['foo', 'bar'])
        def arg_same():
            """session scoped fixture"""
        '''
    )
    p = testdir.makepyfile(
        '''
        import pytest
        @pytest.fixture(scope='function')
        def arg_other(arg_same):
            """function scoped fixture"""
        def test_arg1(arg_other):
            pass
    '''
    )

    result = testdir.runpytest(mode, p)
    assert result.ret == 0

    result.stdout.fnmatch_lines(
        [
            "SETUP    S arg_same?foo?",
            "TEARDOWN S arg_same?foo?",
            "SETUP    S arg_same?bar?",
            "TEARDOWN S arg_same?bar?",
        ]
    )


def test_show_fixtures_with_parameter_ids(testdir, mode):
    testdir.makeconftest(
        '''
        import pytest
        @pytest.fixture(
            scope='session', params=['foo', 'bar'], ids=['spam', 'ham'])
        def arg_same():
            """session scoped fixture"""
        '''
    )
    p = testdir.makepyfile(
        '''
        import pytest
        @pytest.fixture(scope='function')
        def arg_other(arg_same):
            """function scoped fixture"""
        def test_arg1(arg_other):
            pass
    '''
    )

    result = testdir.runpytest(mode, p)
    assert result.ret == 0

    result.stdout.fnmatch_lines(
        ["SETUP    S arg_same?spam?", "SETUP    S arg_same?ham?"]
    )


def test_show_fixtures_with_parameter_ids_function(testdir, mode):
    """
    This function tests the `show_fixtures_with_parameter_ids` functionality in a pytest environment. It creates a fixture with multiple parameters and custom IDs, then runs a test to ensure the fixture is properly set up.
    
    Parameters:
    - testdir: The pytest test directory object used to create and run tests.
    - mode: The mode in which pytest is run.
    
    The function creates a Python file with a fixture that has multiple parameters ('foo' and 'bar') and custom IDs generated by a lambda function.
    """

    p = testdir.makepyfile(
        """
        import pytest
        @pytest.fixture(params=['foo', 'bar'], ids=lambda p: p.upper())
        def foobar():
            pass
        def test_foobar(foobar):
            pass
    """
    )

    result = testdir.runpytest(mode, p)
    assert result.ret == 0

    result.stdout.fnmatch_lines(["*SETUP    F foobar?FOO?", "*SETUP    F foobar?BAR?"])


def test_dynamic_fixture_request(testdir):
    p = testdir.makepyfile(
        """
        import pytest
        @pytest.fixture()
        def dynamically_requested_fixture():
            pass
        @pytest.fixture()
        def dependent_fixture(request):
            request.getfixturevalue('dynamically_requested_fixture')
        def test_dyn(dependent_fixture):
            pass
    """
    )

    result = testdir.runpytest("--setup-only", p)
    assert result.ret == 0

    result.stdout.fnmatch_lines(
        [
            "*SETUP    F dynamically_requested_fixture",
            "*TEARDOWN F dynamically_requested_fixture",
        ]
    )


def test_capturing(testdir):
    """
    Tests the capturing of stdout and stderr during fixture setup.
    
    This function runs a pytest test with a custom fixture that writes to both stdout and stderr. The test is run with the `--setup-only` flag to capture the output during the fixture setup phase. The expected output is verified using `fnmatch_lines`.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest fixture that provides a test directory for running tests.
    
    Returns:
    - None: The function asserts that the expected output is captured during the
    """

    p = testdir.makepyfile(
        """
        import pytest, sys
        @pytest.fixture()
        def one():
            sys.stdout.write('this should be captured')
            sys.stderr.write('this should also be captured')
        @pytest.fixture()
        def two(one):
            assert 0
        def test_capturing(two):
            pass
    """
    )

    result = testdir.runpytest("--setup-only", p)
    result.stdout.fnmatch_lines(
        ["this should be captured", "this should also be captured"]
    )


def test_show_fixtures_and_execute_test(testdir):
    """ Verifies that setups are shown and tests are executed. """
    p = testdir.makepyfile(
        """
        import pytest
        @pytest.fixture
        def arg():
            assert True
        def test_arg(arg):
            assert False
    """
    )

    result = testdir.runpytest("--setup-show", p)
    assert result.ret == 1

    result.stdout.fnmatch_lines(
        ["*SETUP    F arg*", "*test_arg (fixtures used: arg)F*", "*TEARDOWN F arg*"]
    )
