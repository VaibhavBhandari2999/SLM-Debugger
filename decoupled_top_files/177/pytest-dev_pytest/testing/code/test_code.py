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
    """
    Test that two Code objects are not equal if their compiled code is different.
    
    Args:
    None
    
    Returns:
    None
    
    Raises:
    AssertionError: If the two Code objects are equal when they should not be.
    
    Important Functions:
    - `Code`
    - `compile`
    - `assert`
    
    Variables:
    - `code1`: A Code object containing the compiled code 'foo = "bar"'.
    - `code2`: A Code object containing the compiled
    """

    code1 = Code(compile('foo = "bar"', "", "exec"))
    assert code1 == code1
    code2 = Code(compile('foo = "baz"', "", "exec"))
    assert code2 != code1


def test_code_gives_back_name_for_not_existing_file() -> None:
    """
    Generate a Python docstring for the provided function.
    
    Args:
    None
    
    Returns:
    A string containing the generated docstring.
    
    Summary:
    This function tests if the given code returns the correct filename for a non-existing file. It uses the `compile` function to create a code object with a specified name and then checks if the `co_filename` attribute of the code object matches the specified name. It also creates an instance of the `Code` class with the compiled code and
    """

    name = "abc-123"
    co_code = compile("pass\n", name, "exec")
    assert co_code.co_filename == name
    code = Code(co_code)
    assert str(code.path) == name
    assert code.fullsource is None


def test_code_with_class() -> None:
    """
    Test code with class.
    
    Args:
    None
    
    Returns:
    None
    
    Raises:
    TypeError: If the input is not of the expected type.
    
    Notes:
    - The function creates a class 'A' using the 'class' keyword.
    - The 'pytest.raises' function is used to assert that a specific exception (TypeError) is raised when calling the 'Code' function with an instance of class 'A'.
    """

    class A:
        pass

    pytest.raises(TypeError, Code, A)


def x() -> None:
    raise NotImplementedError()


def test_code_fullsource() -> None:
    """
    Generate a Python docstring for the provided function.
    
    Args:
    code (Code): The Code object containing the function to be documented.
    
    Returns:
    str: The generated Python docstring.
    """

    code = Code(x)
    full = code.fullsource
    assert "test_code_fullsource()" in str(full)


def test_code_source() -> None:
    """
    def x() -> None:
    raise NotImplementedError()
    """

    code = Code(x)
    src = code.source()
    expected = """def x() -> None:
    raise NotImplementedError()"""
    assert str(src) == expected


def test_frame_getsourcelineno_myself() -> None:
    """
    Test that the frame's getsource and getsourcefile methods return the correct values.
    
    This function defines a nested function `func` that returns the current frame using `sys._getframe(0)`. It then creates a `Frame` object from this frame and retrieves the source code and line number. The assertions check that the source code is not `None` and that the line containing the return statement starts with the expected string.
    
    Important functions:
    - `sys._getframe
    """

    def func() -> FrameType:
        return sys._getframe(0)

    f = Frame(func())
    source, lineno = f.code.fullsource, f.lineno
    assert source is not None
    assert source[lineno].startswith("        return sys._getframe(0)")


def test_getstatement_empty_fullsource() -> None:
    """
    Tests the `statement` attribute of a frame object when the `fullsource` attribute is set to `None`.
    
    This function creates a frame object using the `func` function, which returns the current frame. It then patches the `fullsource` attribute of the code object associated with the frame to `None`. Finally, it asserts that the `statement` attribute of the frame is an empty string.
    
    Important Functions:
    - `sys._getframe`: Used to get the current frame
    """

    def func() -> FrameType:
        return sys._getframe(0)

    f = Frame(func())
    with mock.patch.object(f.code.__class__, "fullsource", None):
        assert f.statement == ""


def test_code_from_func() -> None:
    """
    Generate a Python docstring for the provided function.
    
    Args:
    func (function): The function to generate a docstring for.
    
    Returns:
    str: The generated docstring.
    """

    co = Code(test_frame_getsourcelineno_myself)
    assert co.firstlineno
    assert co.path


def test_unicode_handling() -> None:
    """
    Test handling of Unicode strings.
    
    Args:
    None
    
    Returns:
    None
    
    Raises:
    Exception: Raised with a Unicode-encoded string as the argument.
    
    Summary:
    This function tests how the system handles Unicode strings by encoding
    the string "ąć" and raising an exception with this encoded value. The
    `pytest.raises` context manager is used to capture the raised exception,
    and the string representation of the captured exception information is
    returned.
    """

    value = "ąć".encode()

    def f() -> None:
        raise Exception(value)

    excinfo = pytest.raises(Exception, f)
    str(excinfo)


def test_code_getargs() -> None:
    """
    Tests the `getargs` method of the `Code` class.
    
    The `getargs` method is expected to return the arguments of a function,
    including variable-length arguments and keyword arguments.
    
    Args:
    None
    
    Returns:
    None
    
    Examples:
    >>> from your_module import Code
    >>> def f1(x):
    ...     raise NotImplementedError()
    >>> c1 = Code(f1)
    >>> c1.getargs(var=True)
    ('x',)
    >>>
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
    """
    Get the arguments of a frame.
    
    Args:
    var (bool): If True, return variable names and values; otherwise, return only the names.
    
    Returns:
    list: A list of tuples containing the argument names and their corresponding values if `var` is True, or just the argument names if `var` is False.
    """

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
        """
        Test the behavior of `getsource` when encountering an assertion error.
        
        This function attempts to retrieve the source code of a block of code that
        contains an assertion failure. It is expected to raise an `AssertionError`
        and capture the exception information using `ExceptionInfo.from_current()`.
        The test verifies that the exception representation can be obtained using
        `getrepr()`.
        
        Args:
        None
        
        Returns:
        None
        """

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
        Tests the getsource method by creating an assertion error, capturing the traceback, and verifying the source code snippet matches the expected length and content.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the source code snippet does not match the expected length or content.
        
        Important Functions:
        - `ExceptionInfo.from_current()`: Captures the current exception information.
        - `entry.getsource()`: Retrieves the source code snippet from the traceback entry.
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
        """
        Tests that the `ReprFuncArgs` class correctly formats arguments with mixed encodings when using the `toterminal` method.
        
        Args:
        tw_mock (Mock): A mock object representing the terminal writer.
        
        Returns:
        None
        
        Important Functions:
        - `ReprFuncArgs`: The class used to format arguments.
        - `toterminal`: The method of the `ReprFuncArgs` class that formats and writes the arguments to the terminal.
        
        Input Variables
        """

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
