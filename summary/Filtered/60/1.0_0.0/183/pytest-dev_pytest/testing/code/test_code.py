import re
import sys
from types import FrameType
from unittest import mock

import pytest
from _pytest._code import Code
from _pytest._code import ExceptionInfo
from _pytest._code import Frame
from _pytest._code import Source
from _pytest._code.code import ExceptionChainRepr
from _pytest._code.code import ReprFuncArgs


def test_ne() -> None:
    code1 = Code(compile('foo = "bar"', "", "exec"))
    assert code1 == code1
    code2 = Code(compile('foo = "baz"', "", "exec"))
    assert code2 != code1


def test_code_gives_back_name_for_not_existing_file() -> None:
    """
    This function tests if the provided code generates the correct filename for a non-existing file. It compiles a simple 'pass' statement with a given name and checks if the compiled code's filename matches the provided name. It then creates an instance of the Code class with the compiled code and asserts that the path of the code object matches the provided name. Additionally, it checks if the full source of the code is None.
    
    Key Parameters:
    - name (str): The name of the file for the compiled
    """

    name = "abc-123"
    co_code = compile("pass\n", name, "exec")
    assert co_code.co_filename == name
    code = Code(co_code)
    assert str(code.path) == name
    assert code.fullsource is None


def test_code_from_function_with_class() -> None:
    class A:
        pass

    with pytest.raises(TypeError):
        Code.from_function(A)


def x() -> None:
    raise NotImplementedError()


def test_code_fullsource() -> None:
    """
    Generate a Python docstring for the provided function.
    
    This function takes a function `x` and returns a Code object initialized with the function `x`. The `fullsource` attribute of the Code object is then extracted and checked to ensure it contains the string "test_code_fullsource()".
    
    Parameters:
    x (function): The function to be used for initializing the Code object.
    
    Returns:
    None: This function does not return any value. It performs a check on the `fullsource` attribute
    """

    code = Code.from_function(x)
    full = code.fullsource
    assert "test_code_fullsource()" in str(full)


def test_code_source() -> None:
    code = Code.from_function(x)
    src = code.source()
    expected = """def x() -> None:
    raise NotImplementedError()"""
    assert str(src) == expected


def test_frame_getsourcelineno_myself() -> None:
    def func() -> FrameType:
        return sys._getframe(0)

    f = Frame(func())
    source, lineno = f.code.fullsource, f.lineno
    assert source is not None
    assert source[lineno].startswith("        return sys._getframe(0)")


def test_getstatement_empty_fullsource() -> None:
    """
    Tests the `getstatement` method of a `Frame` object when the `fullsource` attribute is set to `None`.
    
    This function defines a test case where a function `func` is created and its frame is obtained. The `fullsource` attribute of the code object within the frame is then mocked to be `None`. The `getstatement` method of the frame is called and it is expected to return an empty string, indicating that no source code is available for the frame's statement
    """

    def func() -> FrameType:
        return sys._getframe(0)

    f = Frame(func())
    with mock.patch.object(f.code.__class__, "fullsource", None):
        assert f.statement == Source("")


def test_code_from_func() -> None:
    co = Code.from_function(test_frame_getsourcelineno_myself)
    assert co.firstlineno
    assert co.path


def test_unicode_handling() -> None:
    value = "ąć".encode()

    def f() -> None:
        raise Exception(value)

    excinfo = pytest.raises(Exception, f)
    str(excinfo)


def test_code_getargs() -> None:
    """
    Extracts and returns the arguments of a function.
    
    This function takes a function and returns a tuple containing the names of the arguments, including positional, variable positional, keyword, and variable keyword arguments.
    
    Args:
    f (function): The function from which to extract the argument names.
    
    Returns:
    tuple: A tuple containing the names of the arguments.
    """

    def f1(x):
        raise NotImplementedError()

    c1 = Code.from_function(f1)
    assert c1.getargs(var=True) == ("x",)

    def f2(x, *y):
        raise NotImplementedError()

    c2 = Code.from_function(f2)
    assert c2.getargs(var=True) == ("x", "y")

    def f3(x, **z):
        raise NotImplementedError()

    c3 = Code.from_function(f3)
    assert c3.getargs(var=True) == ("x", "z")

    def f4(x, *y, **z):
        raise NotImplementedError()

    c4 = Code.from_function(f4)
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

    def test_tb_entry_str(self):
        try:
            assert False
        except AssertionError:
            exci = ExceptionInfo.from_current()
        pattern = r"  File '.*test_code.py':\d+ in test_tb_entry_str\n  assert False"
        entry = str(exci.traceback[0])
        assert re.match(pattern, entry)


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
