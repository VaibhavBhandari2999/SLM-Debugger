from _pytest.pytester import Pytester


def test_no_items_should_not_show_output(pytester: Pytester) -> None:
    """
    Tests if the pytester fixture runs a test with no fixtures and does not show any output related to fixtures used by the test. The function uses the `pytester` fixture to run the test and checks that the output does not contain any lines matching the pattern "*fixtures used by*". The function returns 0 if the test passes, indicating no fixtures were used and no output was shown, otherwise it returns a non-zero value.
    
    Parameters:
    - pytester (Pytester): A fixture provided by
    """

    result = pytester.runpytest("--fixtures-per-test")
    result.stdout.no_fnmatch_line("*fixtures used by*")
    assert result.ret == 0


def test_fixtures_in_module(pytester: Pytester) -> None:
    """
    Test fixtures in a module.
    
    This test checks the functionality of using fixtures within a module, specifically focusing on the visibility and documentation of these fixtures when used in tests. The test creates a module with two fixtures: one hidden and one public, and then runs pytest with the `--fixtures-per-test` option to verify that only the public fixture is documented in the test output.
    
    Key Parameters:
    - `pytester`: A Pytester fixture used to create and run test files.
    
    Summary:
    - A module
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
            "arg1 -- test_fixtures_in_module.py:6",
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
            "arg2 -- conftest.py:6",
            "    arg2 docstring",
            "*fixtures used by test_arg3*",
            "*(test_fixtures_in_conftest.py:4)*",
            "arg1 -- conftest.py:3",
            "    arg1 docstring",
            "arg2 -- conftest.py:6",
            "    arg2 docstring",
            "arg3 -- conftest.py:9",
            "    arg3",
        ]
    )


def test_should_show_fixtures_used_by_test(pytester: Pytester) -> None:
    """
    Tests the functionality of showing fixtures used by a test.
    
    This function checks if the pytester fixture can be used to run pytest with specific options and verify the output for a test that uses fixtures. The test module and conftest file are created dynamically to test the functionality.
    
    Parameters:
    pytester (Pytester): A fixture that provides methods to create and run pytest tests.
    
    Returns:
    None: The function asserts the expected output through stdout matchers.
    """

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
            "arg1 -- test_should_show_fixtures_used_by_test.py:3",
            "    arg1 from testmodule",
            "arg2 -- conftest.py:6",
            "    arg2 from conftest",
        ]
    )


def test_verbose_include_private_fixtures_and_loc(pytester: Pytester) -> None:
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


def test_multiline_docstring_in_module(pytester: Pytester) -> None:
    p = pytester.makepyfile(
        '''
        import pytest
        @pytest.fixture
        def arg1():
            """Docstring content that spans across multiple lines,
            through second line,
            and through third line.

            Docstring content that extends into a second paragraph.

            Docstring content that extends into a third paragraph.
            """
        def test_arg1(arg1):
            pass
    '''
    )

    result = pytester.runpytest("--fixtures-per-test", p)
    assert result.ret == 0

    result.stdout.fnmatch_lines(
        [
            "*fixtures used by test_arg1*",
            "*(test_multiline_docstring_in_module.py:13)*",
            "arg1 -- test_multiline_docstring_in_module.py:3",
            "    Docstring content that spans across multiple lines,",
            "    through second line,",
            "    and through third line.",
        ]
    )


def test_verbose_include_multiline_docstring(pytester: Pytester) -> None:
    p = pytester.makepyfile(
        '''
        import pytest
        @pytest.fixture
        def arg1():
            """Docstring content that spans across multiple lines,
            through second line,
            and through third line.

            Docstring content that extends into a second paragraph.

            Docstring content that extends into a third paragraph.
            """
        def test_arg1(arg1):
            pass
    '''
    )

    result = pytester.runpytest("--fixtures-per-test", "-v", p)
    assert result.ret == 0

    result.stdout.fnmatch_lines(
        [
            "*fixtures used by test_arg1*",
            "*(test_verbose_include_multiline_docstring.py:13)*",
            "arg1 -- test_verbose_include_multiline_docstring.py:3",
            "    Docstring content that spans across multiple lines,",
            "    through second line,",
            "    and through third line.",
            "    ",
            "    Docstring content that extends into a second paragraph.",
            "    ",
            "    Docstring content that extends into a third paragraph.",
        ]
    )
rd paragraph.",
        ]
    )
