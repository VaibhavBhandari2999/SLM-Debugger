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
    Test the non-equality of two code objects.
    
    This function compares two code objects generated from different source strings.
    It checks if the two code objects are not equal.
    
    Parameters:
    code1 (_pytest._code.Code): The first code object to compare.
    code2 (_pytest._code.Code): The second code object to compare.
    
    Returns:
    bool: True if the code objects are not equal, False otherwise.
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
    """
    This function tests the `_getstatement` method of a `_code.Frame` object when the `fullsource` attribute of the code object is `None`.
    
    Parameters:
    - None
    
    Returns:
    - The statement as a string. In this case, it should return an empty string ("") because the `fullsource` attribute is `None`.
    
    This function is useful for verifying that the `_getstatement` method correctly handles cases where the source code is not available.
    """

    def func():
        return sys._getframe(0)

    f = func()
    f = _pytest._code.Frame(f)
    with mock.patch.object(f.code.__class__, "fullsource", None):
        assert f.statement == ""


def test_code_from_func():
    co = _pytest._code.Code(test_frame_getsourcelineno_myself)
    assert co.firstlineno
    assert co.path


def test_unicode_handling():
    """
    Test Unicode Handling
    
    This function encodes a Unicode string and raises an exception with the encoded value. It then captures the exception and performs operations to convert the exception information to text and bytes types.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    Exception: The exception raised with the encoded Unicode string.
    
    Notes:
    - The function uses the 'u"ąć"' Unicode string.
    - The string is encoded in UTF-8.
    - The exception is captured and converted to
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
        """
        Test the `getsource` function with a bad assertion.
        
        This test attempts to retrieve the source code of a function that contains an `AssertionError`. The test intentionally includes an `AssertionError` to ensure that the `getsource` function can handle exceptions properly.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the `getsource` function does not handle the exception correctly.
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
