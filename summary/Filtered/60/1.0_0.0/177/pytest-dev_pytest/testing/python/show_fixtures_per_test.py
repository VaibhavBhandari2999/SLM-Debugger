def test_no_items_should_not_show_output(testdir):
    """
    Tests that when no items are provided to pytest, the output indicating fixtures used by tests is not shown.
    
    Parameters:
    testdir (pytest.Testdir): A pytest fixture that provides a temporary test directory.
    
    Returns:
    None: The function asserts that the output does not contain the phrase "fixtures used by" and that the test run was successful (exit code 0).
    """

    result = testdir.runpytest("--fixtures-per-test")
    result.stdout.no_fnmatch_line("*fixtures used by*")
    assert result.ret == 0


def test_fixtures_in_module(testdir):
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

    result = testdir.runpytest("--fixtures-per-test", p)
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


def test_fixtures_in_conftest(testdir):
    """
    Function to test fixtures in conftest.
    
    This function creates a conftest file with fixture definitions and a test file with test functions. It then runs pytest with the `--fixtures-per-test` option to display the fixtures used by each test.
    
    Parameters:
    testdir (pytest.Testdir): The pytest test directory object.
    
    Returns:
    None: The function does not return anything, but it prints the fixtures used by each test.
    """

    testdir.makeconftest(
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
    p = testdir.makepyfile(
        """
        def test_arg2(arg2):
            pass
        def test_arg3(arg3):
            pass
    """
    )
    result = testdir.runpytest("--fixtures-per-test", p)
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


def test_should_show_fixtures_used_by_test(testdir):
    testdir.makeconftest(
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
    p = testdir.makepyfile(
        '''
        import pytest
        @pytest.fixture
        def arg1():
            """arg1 from testmodule"""
        def test_args(arg1, arg2):
            pass
    '''
    )
    result = testdir.runpytest("--fixtures-per-test", p)
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


def test_verbose_include_private_fixtures_and_loc(testdir):
    """
    Tests the verbose inclusion of private fixtures and local arguments in a test function. The function checks if the fixtures from the conftest and local arguments are correctly included and displayed in the verbose output.
    
    Key Parameters:
    - `testdir`: The pytest test directory object used to create and run tests.
    
    The function creates a conftest file with private fixtures and a test file with a test function that uses both private fixtures and local arguments. It then runs pytest with the `--fixtures-per-test` and
    """

    testdir.makeconftest(
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
    p = testdir.makepyfile(
        '''
        import pytest
        @pytest.fixture
        def arg3():
            """arg3 from testmodule"""
        def test_args(arg2, arg3):
            pass
    '''
    )
    result = testdir.runpytest("--fixtures-per-test", "-v", p)
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


def test_doctest_items(testdir):
    testdir.makepyfile(
        '''
        def foo():
            """
            >>> 1 + 1
            2
            """
    '''
    )
    testdir.maketxtfile(
        """
        >>> 1 + 1
        2
    """
    )
    result = testdir.runpytest(
        "--fixtures-per-test", "--doctest-modules", "--doctest-glob=*.txt", "-v"
    )
    assert result.ret == 0

    result.stdout.fnmatch_lines(["*collected 2 items*"])
