from _pytest.pytester import Pytester


def test_no_items_should_not_show_output(pytester: Pytester) -> None:
    result = pytester.runpytest("--fixtures-per-test")
    result.stdout.no_fnmatch_line("*fixtures used by*")
    assert result.ret == 0


def test_fixtures_in_module(pytester: Pytester) -> None:
    """
    Tests the behavior of fixtures in a module.
    
    This test function runs pytest with the `--fixtures-per-test` option on a module containing two fixtures: `_arg0` and `arg1`. The test checks that the `arg1` fixture is correctly documented and used in a test function, while the `_arg0` fixture is not included in the output. The test ensures that only the relevant fixtures are displayed, adhering to the documentation and usage within the test module.
    """

    p = pytester.makepyfile(
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

    result = pytester.runpytest("--fixtures-per-test", p)
    assert result.ret == 0

    result.stdout.fnmatch_lines(
        [
            "*fixtures used by test_arg1*",
            "*(test_fixtures_in_module.py:9)*",
            "arg1",
            "    arg1 docstring",
        ]
    )
    result.stdout.no_fnmatch_line("*_arg0*")


def test_fixtures_in_conftest(pytester: Pytester) -> None:
    pytester.makeconftest(
        '''
        import pytest
        @pytest.fixture
        def arg1():
            """arg1 docstring"""
        @pytest.fixture
        def arg2():
            """arg2 docstring"""
        @pytest.fixture
        def arg3(arg1, arg2):
            """arg3
            docstring
            """
    '''
    )
    p = pytester.makepyfile(
        """
        def test_arg2(arg2):
            pass
        def test_arg3(arg3):
            pass
    """
    )
    result = pytester.runpytest("--fixtures-per-test", p)
    assert result.ret == 0

    result.stdout.fnmatch_lines(
        [
            "*fixtures used by test_arg2*",
            "*(test_fixtures_in_conftest.py:2)*",
            "arg2",
            "    arg2 docstring",
            "*fixtures used by test_arg3*",
            "*(test_fixtures_in_conftest.py:4)*",
            "arg1",
            "    arg1 docstring",
            "arg2",
            "    arg2 docstring",
            "arg3",
            "    arg3",
            "    docstring",
        ]
    )


def test_should_show_fixtures_used_by_test(pytester: Pytester) -> None:
    pytester.makeconftest(
        '''
        import pytest
        @pytest.fixture
        def arg1():
            """arg1 from conftest"""
        @pytest.fixture
        def arg2():
            """arg2 from conftest"""
    '''
    )
    p = pytester.makepyfile(
        '''
        import pytest
        @pytest.fixture
        def arg1():
            """arg1 from testmodule"""
        def test_args(arg1, arg2):
            pass
    '''
    )
    result = pytester.runpytest("--fixtures-per-test", p)
    assert result.ret == 0

    result.stdout.fnmatch_lines(
        [
            "*fixtures used by test_args*",
            "*(test_should_show_fixtures_used_by_test.py:6)*",
            "arg1",
            "    arg1 from testmodule",
            "arg2",
            "    arg2 from conftest",
        ]
    )


def test_verbose_include_private_fixtures_and_loc(pytester: Pytester) -> None:
    """
    Tests the verbose inclusion of private fixtures and local arguments in a test function.
    
    This function runs a test with verbose output to include private fixtures and local arguments. It checks that the correct fixtures and their descriptions are included in the output.
    
    Args:
    pytester (Pytester): A fixture provided by the `pytester` package for creating and running tests.
    
    Returns:
    None: The function asserts that the test output matches the expected results.
    """

    pytester.makeconftest(
        '''
        import pytest
        @pytest.fixture
        def _arg1():
            """_arg1 from conftest"""
        @pytest.fixture
        def arg2(_arg1):
            """arg2 from conftest"""
    '''
    )
    p = pytester.makepyfile(
        '''
        import pytest
        @pytest.fixture
        def arg3():
            """arg3 from testmodule"""
        def test_args(arg2, arg3):
            pass
    '''
    )
    result = pytester.runpytest("--fixtures-per-test", "-v", p)
    assert result.ret == 0

    result.stdout.fnmatch_lines(
        [
            "*fixtures used by test_args*",
            "*(test_verbose_include_private_fixtures_and_loc.py:6)*",
            "_arg1 -- conftest.py:3",
            "    _arg1 from conftest",
            "arg2 -- conftest.py:6",
            "    arg2 from conftest",
            "arg3 -- test_verbose_include_private_fixtures_and_loc.py:3",
            "    arg3 from testmodule",
        ]
    )


def test_doctest_items(pytester: Pytester) -> None:
    pytester.makepyfile(
        '''
        def foo():
            """
            >>> 1 + 1
            2
            """
    '''
    )
    pytester.maketxtfile(
        """
        >>> 1 + 1
        2
    """
    )
    result = pytester.runpytest(
        "--fixtures-per-test", "--doctest-modules", "--doctest-glob=*.txt", "-v"
    )
    assert result.ret == 0

    result.stdout.fnmatch_lines(["*collected 2 items*"])
