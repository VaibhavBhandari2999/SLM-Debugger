import sys
from types import FrameType
from unittest import mock

import pytest
from _pytest._code import Code
from _pytest._code import ExceptionInfo
from _pytest._code import Frame
from _pytest._code.code import ExceptionChainRepr
from _pytest._code.code import ReprFuncArgs


def test_ne() -> None:
    code1 = Code(compile('foo = "bar"', "", "exec"))
    assert code1 == code1
    code2 = Code(compile('foo = "baz"', "", "exec"))
    assert code2 != code1


def test_code_gives_back_name_for_not_existing_file() -> None:
    """
    Tests if the provided code returns the correct filename for a non-existing file.
    
    This function compiles a simple 'pass' statement into a code object with a specified filename. It then checks if the filename is correctly reflected in the code object and in a custom `Code` object. The `Code` object is instantiated with the compiled code and is expected to return the same filename.
    
    Parameters:
    None
    
    Returns:
    None
    """

    name = "abc-123"
    co_code = compile("pass\n", name, "exec")
    assert co_code.co_filename == name
    code = Code(co_code)
    assert str(code.path) == name
    assert code.fullsource is None


def test_code_with_class() -> None:
    class A:
        pass

    pytest.raises(TypeError, Code, A)


def x() -> None:
    raise NotImplementedError()


def test_code_fullsource() -> None:
    code = Code(x)
    full = code.fullsource
    assert "test_code_fullsource()" in str(full)


def test_code_source() -> None:
    code = Code(x)
    src = code.source()
    expected = """def x() -> None:
    raise NotImplementedError()"""
    assert str(src) == expected


def test_frame_getsourcelineno_myself() -> None:
    """
    Get the current frame and retrieve its source code and line number.
    
    This function defines a nested function `func` that returns the current frame using `sys._getframe(0)`. It then creates a Frame object `f` from the returned frame. The source code and line number of the frame are extracted and stored in variables `source` and `lineno`, respectively. The function asserts that the source code is not None and that the line at `lineno` starts with the expected string.
    
    Parameters
    """

    def func() -> FrameType:
        return sys._getframe(0)

    f = Frame(func())
    source, lineno = f.code.fullsource, f.lineno
    assert source is not None
    assert source[lineno].startswith("        return sys._getframe(0)")


def test_getstatement_empty_fullsource() -> None:
    def func() -> FrameType:
        return sys._getframe(0)

    f = Frame(func())
    with mock.patch.object(f.code.__class__, "fullsource", None):
        assert f.statement == ""


def test_code_from_func() -> None:
    co = Code(test_frame_getsourcelineno_myself)
    assert co.firstlineno
    assert co.path


def test_unicode_handling() -> None:
    """
    Tests handling of Unicode strings in exceptions.
    
    This function encodes a string containing non-ASCII characters and raises an exception with this encoded string. It then captures the exception and converts it to a string for further processing or inspection.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    Exception: An exception containing an encoded Unicode string.
    
    Usage:
    This function is primarily used for testing how Python handles Unicode strings within exceptions. It can be called to ensure that the encoding and handling of such strings
    """

    value = "ąć".encode()

    def f() -> None:
        raise Exception(value)

    excinfo = pytest.raises(Exception, f)
    str(excinfo)


def test_code_getargs() -> None:
    """
    Get the arguments of a function.
    
    This function extracts the arguments of a given function, including positional
    arguments, variable-length argument lists, and keyword arguments. It returns
    a tuple of argument names.
    
    Parameters:
    f (function): The function from which to extract the arguments.
    
    Returns:
    tuple: A tuple containing the argument names of the function.
    """

    def f1(x):
        raise NotImplementedError()

    c1 = Code(f1)
    assert c1.getargs(var=True) == ("x",)

    def f2(x, *y):
        raise NotImplementedError()

    c2 = Code(f2)
    assert c2.getargs(var=True) == ("x", "y")

    def f3(x, **z):
        raise NotImplementedError()

    c3 = Code(f3)
    assert c3.getargs(var=True) == ("x", "z")

    def f4(x, *y, **z):
        raise NotImplementedError()

    c4 = Code(f4)
    assert c4.getargs(var=True) == ("x", "y", "z")


def test_frame_getargs() -> None:
    def f1(x) -> FrameType:
        return sys._getframe(0)

    fr1 = Frame(f1("a"))
    assert fr1.getargs(var=True) == [("x", "a")]

    def f2(x, *y) -> FrameType:
        return sys._getframe(0)

    fr2 = Frame(f2("a", "b", "c"))
    assert fr2.getargs(var=True) == [("x", "a"), ("y", ("b", "c"))]

    def f3(x, **z) -> FrameType:
        return sys._getframe(0)

    fr3 = Frame(f3("a", b="c"))
    assert fr3.getargs(var=True) == [("x", "a"), ("z", {"b": "c"})]

    def f4(x, *y, **z) -> FrameType:
        return sys._getframe(0)

    fr4 = Frame(f4("a", "b", c="d"))
    assert fr4.getargs(var=True) == [("x", "a"), ("y", ("b",)), ("z", {"c": "d"})]


class TestExceptionInfo:
    def test_bad_getsource(self) -> None:
        try:
            if False:
                pass
            else:
                assert False
        except AssertionError:
            exci = ExceptionInfo.from_current()
        assert exci.getrepr()

    def test_from_current_with_missing(self) -> None:
        with pytest.raises(AssertionError, match="no current exception"):
            ExceptionInfo.from_current()


class TestTracebackEntry:
    def test_getsource(self) -> None:
        """
        Test the getsource method for retrieving the source code of an exception traceback entry.
        
        This method checks that the source code retrieved from an exception traceback entry is as expected.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The source code retrieved should not be None.
        - The length of the source code should be 6.
        - The source code should contain the string 'assert False'.
        """

        try:
            if False:
                pass
            else:
                assert False
        except AssertionError:
            exci = ExceptionInfo.from_current()
        entry = exci.traceback[0]
        source = entry.getsource()
        assert source is not None
        assert len(source) == 6
        assert "assert False" in source[5]


class TestReprFuncArgs:
    def test_not_raise_exception_with_mixed_encoding(self, tw_mock) -> None:
        args = [("unicode_string", "São Paulo"), ("utf8_string", b"S\xc3\xa3o Paulo")]

        r = ReprFuncArgs(args)
        r.toterminal(tw_mock)

        assert (
            tw_mock.lines[0]
            == r"unicode_string = São Paulo, utf8_string = b'S\xc3\xa3o Paulo'"
        )


def test_ExceptionChainRepr():
    """Test ExceptionChainRepr, especially with regard to being hashable."""
    try:
        raise ValueError()
    except ValueError:
        excinfo1 = ExceptionInfo.from_current()
        excinfo2 = ExceptionInfo.from_current()

    repr1 = excinfo1.getrepr()
    repr2 = excinfo2.getrepr()
    assert repr1 != repr2

    assert isinstance(repr1, ExceptionChainRepr)
    assert hash(repr1) != hash(repr2)
    assert repr1 is not excinfo1.getrepr()
