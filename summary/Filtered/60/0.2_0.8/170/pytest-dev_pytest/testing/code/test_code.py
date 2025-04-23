# coding: utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys

from six import text_type
from test_excinfo import TWMock

import _pytest._code
import pytest

try:
    import mock
except ImportError:
    import unittest.mock as mock


def test_ne():
    """
    Compare two Code objects for equality or inequality.
    
    Parameters:
    code1 (_pytest._code.Code): The first Code object to compare.
    code2 (_pytest._code.Code): The second Code object to compare.
    
    Returns:
    bool: True if the Code objects are equal, False otherwise.
    """

    code1 = _pytest._code.Code(compile('foo = "bar"', "", "exec"))
    assert code1 == code1
    code2 = _pytest._code.Code(compile('foo = "baz"', "", "exec"))
    assert code2 != code1


def test_code_gives_back_name_for_not_existing_file():
    name = "abc-123"
    co_code = compile("pass\n", name, "exec")
    assert co_code.co_filename == name
    code = _pytest._code.Code(co_code)
    assert str(code.path) == name
    assert code.fullsource is None


def test_code_with_class():
    class A(object):
        pass

    pytest.raises(TypeError, _pytest._code.Code, A)


def x():
    raise NotImplementedError()


def test_code_fullsource():
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
    Function to test code from a function.
    
    This function takes a function as input and returns a Code object from it. The Code object contains the first line number and the path of the code.
    
    Parameters:
    test_frame_getsourcelineno_myself (function): The function from which to generate the Code object.
    
    Returns:
    co (Code): A Code object containing the first line number and the path of the input function.
    """

    co = _pytest._code.Code(test_frame_getsourcelineno_myself)
    assert co.firstlineno
    assert co.path


def test_unicode_handling():
    """
    Test unicode handling.
    
    This function encodes a unicode string and raises an exception. It then captures the exception and checks the type of the exception information object. The function also handles different Python versions by using `sys.version_info`.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    Exception: The exception raised by the function `f`.
    
    Notes:
    - The function `f` raises an exception with a UTF-8 encoded unicode string.
    - The exception information object is converted to a
    """

    value = u"ąć".encode("UTF-8")

    def f():
        raise Exception(value)

    excinfo = pytest.raises(Exception, f)
    text_type(excinfo)
    if sys.version_info < (3,):
        bytes(excinfo)


@pytest.mark.skipif(sys.version_info[0] >= 3, reason="python 2 only issue")
def test_unicode_handling_syntax_error():
    value = u"ąć".encode("UTF-8")

    def f():
        raise SyntaxError("invalid syntax", (None, 1, 3, value))

    excinfo = pytest.raises(Exception, f)
    str(excinfo)
    if sys.version_info[0] < 3:
        text_type(excinfo)


def test_code_getargs():
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


class TestExceptionInfo(object):
    def test_bad_getsource(self):
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


class TestTracebackEntry(object):
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


class TestReprFuncArgs(object):
    def test_not_raise_exception_with_mixed_encoding(self):
        """
        Tests if the function correctly handles mixed encoding without raising an exception.
        
        Args:
        None
        
        Returns:
        None
        
        This function tests the `ReprFuncArgs` class from `_pytest._code.code` module by passing a list of arguments with both unicode and utf8 encoded strings. The function checks if the representation of the arguments is correct based on the Python version. For Python 3, the utf8 string is expected to be represented as a bytes object, while for Python 2, the
        """

        from _pytest._code.code import ReprFuncArgs

        tw = TWMock()

        args = [("unicode_string", u"São Paulo"), ("utf8_string", b"S\xc3\xa3o Paulo")]

        r = ReprFuncArgs(args)
        r.toterminal(tw)
        if sys.version_info[0] >= 3:
            assert (
                tw.lines[0]
                == r"unicode_string = São Paulo, utf8_string = b'S\xc3\xa3o Paulo'"
            )
        else:
            assert tw.lines[0] == "unicode_string = São Paulo, utf8_string = São Paulo"
