import sys
from unittest import mock

from test_excinfo import TWMock

import _pytest._code
import pytest


def test_ne():
    """
    Test the '!=' operator for two Code objects.
    
    Parameters:
    code1 (_pytest._code.Code): The first Code object.
    code2 (_pytest._code.Code): The second Code object.
    
    Returns:
    bool: True if the two Code objects are not equal, False otherwise.
    """

    code1 = _pytest._code.Code(compile('foo = "bar"', "", "exec"))
    assert code1 == code1
    code2 = _pytest._code.Code(compile('foo = "baz"', "", "exec"))
    assert code2 != code1


def test_code_gives_back_name_for_not_existing_file():
    """
    This function tests whether the provided code object gives back the correct filename for a non-existing file. It compiles a simple 'pass' statement with a specified name, checks the filename attribute, and then creates a Code object from the compiled code. The function asserts that the filename matches the provided name and that the full source is None. The input is a string representing the name of the file, and the output is a boolean indicating whether the test passed.
    
    Parameters:
    name (str): The name of
    """

    name = "abc-123"
    co_code = compile("pass\n", name, "exec")
    assert co_code.co_filename == name
    code = _pytest._code.Code(co_code)
    assert str(code.path) == name
    assert code.fullsource is None


def test_code_with_class():
    class A:
        pass

    pytest.raises(TypeError, _pytest._code.Code, A)


def x():
    raise NotImplementedError()


def test_code_fullsource():
    """
    Generate a Code object from a given variable and retrieve its full source code.
    
    Parameters:
    x (any): The variable from which to generate a Code object.
    
    Returns:
    str: The full source code of the variable as a string.
    
    Example:
    >>> test_code_fullsource()
    'The full source code of the variable x is retrieved and returned as a string.'
    """

    code = _pytest._code.Code(x)
    full = code.fullsource
    assert "test_code_fullsource()" in str(full)


def test_code_source():
    code = _pytest._code.Code(x)
    src = code.source()
    expected = """def x():
    raise NotImplementedError()"""
    assert str(src) == expected


def test_frame_getsourcelineno_myself():
    def func():
        return sys._getframe(0)

    f = func()
    f = _pytest._code.Frame(f)
    source, lineno = f.code.fullsource, f.lineno
    assert source[lineno].startswith("        return sys._getframe(0)")


def test_getstatement_empty_fullsource():
    def func():
        return sys._getframe(0)

    f = func()
    f = _pytest._code.Frame(f)
    with mock.patch.object(f.code.__class__, "fullsource", None):
        assert f.statement == ""


def test_code_from_func():
    """
    Generate a Code object from the provided function and assert its properties.
    
    This function takes a function as input, creates a Code object from it, and asserts that the first line number and file path are present.
    
    Parameters:
    func (function): The function from which to generate the Code object.
    
    Returns:
    None: This function does not return any value, it only performs assertions.
    """

    co = _pytest._code.Code(test_frame_getsourcelineno_myself)
    assert co.firstlineno
    assert co.path


def test_unicode_handling():
    value = "ąć".encode()

    def f():
        raise Exception(value)

    excinfo = pytest.raises(Exception, f)
    str(excinfo)


def test_code_getargs():
    """
    Get the argument names of a function.
    
    This function extracts the argument names from a given function, including
    positional, variable positional, keyword, and variable keyword arguments.
    
    Args:
    f1 (function): A function with positional arguments.
    f2 (function): A function with positional and variable positional arguments.
    f3 (function): A function with positional and keyword arguments.
    f4 (function): A function with positional, variable positional, keyword, and variable keyword arguments.
    
    Returns:
    """

    def f1(x):
        raise NotImplementedError()

    c1 = _pytest._code.Code(f1)
    assert c1.getargs(var=True) == ("x",)

    def f2(x, *y):
        raise NotImplementedError()

    c2 = _pytest._code.Code(f2)
    assert c2.getargs(var=True) == ("x", "y")

    def f3(x, **z):
        raise NotImplementedError()

    c3 = _pytest._code.Code(f3)
    assert c3.getargs(var=True) == ("x", "z")

    def f4(x, *y, **z):
        raise NotImplementedError()

    c4 = _pytest._code.Code(f4)
    assert c4.getargs(var=True) == ("x", "y", "z")


def test_frame_getargs():
    def f1(x):
        return sys._getframe(0)

    fr1 = _pytest._code.Frame(f1("a"))
    assert fr1.getargs(var=True) == [("x", "a")]

    def f2(x, *y):
        return sys._getframe(0)

    fr2 = _pytest._code.Frame(f2("a", "b", "c"))
    assert fr2.getargs(var=True) == [("x", "a"), ("y", ("b", "c"))]

    def f3(x, **z):
        return sys._getframe(0)

    fr3 = _pytest._code.Frame(f3("a", b="c"))
    assert fr3.getargs(var=True) == [("x", "a"), ("z", {"b": "c"})]

    def f4(x, *y, **z):
        return sys._getframe(0)

    fr4 = _pytest._code.Frame(f4("a", "b", c="d"))
    assert fr4.getargs(var=True) == [("x", "a"), ("y", ("b",)), ("z", {"c": "d"})]


class TestExceptionInfo:
    def test_bad_getsource(self):
        """
        Test the getsource function with a bad assertion.
        
        This function attempts to retrieve the source code of an exception that is raised by an `AssertionError`. The test is expected to fail because the `AssertionError` is raised by an unreachable `assert False` statement within an `else` block.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the exception representation cannot be generated.
        
        Note:
        The function relies on the `_pytest._code.ExceptionInfo.from_current()` method
        """

        try:
            if False:
                pass
            else:
                assert False
        except AssertionError:
            exci = _pytest._code.ExceptionInfo.from_current()
        assert exci.getrepr()

    def test_from_current_with_missing(self):
        with pytest.raises(AssertionError, match="no current exception"):
            _pytest._code.ExceptionInfo.from_current()


class TestTracebackEntry:
    def test_getsource(self):
        try:
            if False:
                pass
            else:
                assert False
        except AssertionError:
            exci = _pytest._code.ExceptionInfo.from_current()
        entry = exci.traceback[0]
        source = entry.getsource()
        assert len(source) == 6
        assert "assert False" in source[5]


class TestReprFuncArgs:
    def test_not_raise_exception_with_mixed_encoding(self):
        from _pytest._code.code import ReprFuncArgs

        tw = TWMock()

        args = [("unicode_string", "São Paulo"), ("utf8_string", b"S\xc3\xa3o Paulo")]

        r = ReprFuncArgs(args)
        r.toterminal(tw)

        assert (
            tw.lines[0]
            == r"unicode_string = São Paulo, utf8_string = b'S\xc3\xa3o Paulo'"
        )
