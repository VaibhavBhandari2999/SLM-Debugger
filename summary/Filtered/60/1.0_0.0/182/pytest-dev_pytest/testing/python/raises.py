import re
import sys

import pytest
from _pytest.outcomes import Failed
from _pytest.pytester import Pytester


class TestRaises:
    def test_check_callable(self) -> None:
        with pytest.raises(TypeError, match=r".* must be callable"):
            pytest.raises(RuntimeError, "int('qwe')")  # type: ignore[call-overload]

    def test_raises(self):
        excinfo = pytest.raises(ValueError, int, "qwe")
        assert "invalid literal" in str(excinfo.value)

    def test_raises_function(self):
        excinfo = pytest.raises(ValueError, int, "hello")
        assert "invalid literal" in str(excinfo.value)

    def test_raises_callable_no_exception(self) -> None:
        """
        Tests if a callable object raises a specific exception (ValueError in this case). The function creates a class `A` that is callable and does not raise any exception when called. The `pytest.raises` context manager is used to check if `A()` raises a `ValueError`. If `pytest.raises` does not raise an exception, a `pytest.fail` exception is caught and ignored.
        
        Parameters:
        None
        
        Returns:
        None
        """

        class A:
            def __call__(self):
                pass

        try:
            pytest.raises(ValueError, A())
        except pytest.fail.Exception:
            pass

    def test_raises_falsey_type_error(self) -> None:
        with pytest.raises(TypeError):
            with pytest.raises(AssertionError, match=0):  # type: ignore[call-overload]
                raise AssertionError("ohai")

    def test_raises_repr_inflight(self):
        """Ensure repr() on an exception info inside a pytest.raises with block works (#4386)"""

        class E(Exception):
            pass

        with pytest.raises(E) as excinfo:
            # this test prints the inflight uninitialized object
            # using repr and str as well as pprint to demonstrate
            # it works
            print(str(excinfo))
            print(repr(excinfo))
            import pprint

            pprint.pprint(excinfo)
            raise E()

    def test_raises_as_contextmanager(self, pytester: Pytester) -> None:
        pytester.makepyfile(
            """
            import pytest
            import _pytest._code

            def test_simple():
                with pytest.raises(ZeroDivisionError) as excinfo:
                    assert isinstance(excinfo, _pytest._code.ExceptionInfo)
                    1/0
                print(excinfo)
                assert excinfo.type == ZeroDivisionError
                assert isinstance(excinfo.value, ZeroDivisionError)

            def test_noraise():
                with pytest.raises(pytest.raises.Exception):
                    with pytest.raises(ValueError):
                           int()

            def test_raise_wrong_exception_passes_by():
                with pytest.raises(ZeroDivisionError):
                    with pytest.raises(ValueError):
                           1/0
        """
        )
        result = pytester.runpytest()
        result.stdout.fnmatch_lines(["*3 passed*"])

    def test_does_not_raise(self, pytester: Pytester) -> None:
        """
        Test function to validate the behavior of a division operation with different inputs.
        
        This test function uses parametrization to test the division operation with various inputs and expected outcomes. The `example_input` parameter represents the divisor, and the `expectation` parameter specifies the expected outcome of the division operation, which can either be `does_not_raise()` or `pytest.raises(ZeroDivisionError)`.
        
        Parameters:
        example_input (int): The divisor used in the division operation.
        expectation (Union[does
        """

        pytester.makepyfile(
            """
            from contextlib import contextmanager
            import pytest

            @contextmanager
            def does_not_raise():
                yield

            @pytest.mark.parametrize('example_input,expectation', [
                (3, does_not_raise()),
                (2, does_not_raise()),
                (1, does_not_raise()),
                (0, pytest.raises(ZeroDivisionError)),
            ])
            def test_division(example_input, expectation):
                '''Test how much I know division.'''
                with expectation:
                    assert (6 / example_input) is not None
        """
        )
        result = pytester.runpytest()
        result.stdout.fnmatch_lines(["*4 passed*"])

    def test_does_not_raise_does_raise(self, pytester: Pytester) -> None:
        pytester.makepyfile(
            """
            from contextlib import contextmanager
            import pytest

            @contextmanager
            def does_not_raise():
                yield

            @pytest.mark.parametrize('example_input,expectation', [
                (0, does_not_raise()),
                (1, pytest.raises(ZeroDivisionError)),
            ])
            def test_division(example_input, expectation):
                '''Test how much I know division.'''
                with expectation:
                    assert (6 / example_input) is not None
        """
        )
        result = pytester.runpytest()
        result.stdout.fnmatch_lines(["*2 failed*"])

    def test_noclass(self) -> None:
        with pytest.raises(TypeError):
            pytest.raises("wrong", lambda: None)  # type: ignore[call-overload]

    def test_invalid_arguments_to_raises(self) -> None:
        with pytest.raises(TypeError, match="unknown"):
            with pytest.raises(TypeError, unknown="bogus"):  # type: ignore[call-overload]
                raise ValueError()

    def test_tuple(self):
        with pytest.raises((KeyError, ValueError)):
            raise KeyError("oops")

    def test_no_raise_message(self) -> None:
        """
        Tests the behavior of the `pytest.raises` context manager and function.
        
        This function checks that the `pytest.raises` context manager and function correctly raise a `pytest.fail.Exception` when no exception is raised, as expected.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the `pytest.raises` context manager or function does not raise the expected exception.
        
        Key Points:
        - The function tests two scenarios:
        1. Using `pytest.raises` with a context manager.
        """

        try:
            pytest.raises(ValueError, int, "0")
        except pytest.fail.Exception as e:
            assert e.msg == f"DID NOT RAISE {repr(ValueError)}"
        else:
            assert False, "Expected pytest.raises.Exception"

        try:
            with pytest.raises(ValueError):
                pass
        except pytest.fail.Exception as e:
            assert e.msg == f"DID NOT RAISE {repr(ValueError)}"
        else:
            assert False, "Expected pytest.raises.Exception"

    @pytest.mark.parametrize("method", ["function", "function_match", "with"])
    def test_raises_cyclic_reference(self, method):
        """Ensure pytest.raises does not leave a reference cycle (#1965)."""
        import gc

        class T:
            def __call__(self):
                raise ValueError

        t = T()
        refcount = len(gc.get_referrers(t))

        if method == "function":
            pytest.raises(ValueError, t)
        elif method == "function_match":
            pytest.raises(ValueError, t).match("^$")
        else:
            with pytest.raises(ValueError):
                t()

        # ensure both forms of pytest.raises don't leave exceptions in sys.exc_info()
        assert sys.exc_info() == (None, None, None)

        assert refcount == len(gc.get_referrers(t))

    def test_raises_match(self) -> None:
        msg = r"with base \d+"
        with pytest.raises(ValueError, match=msg):
            int("asdf")

        msg = "with base 10"
        with pytest.raises(ValueError, match=msg):
            int("asdf")

        msg = "with base 16"
        expr = "Regex pattern {!r} does not match \"invalid literal for int() with base 10: 'asdf'\".".format(
            msg
        )
        with pytest.raises(AssertionError, match=re.escape(expr)):
            with pytest.raises(ValueError, match=msg):
                int("asdf", base=10)

        # "match" without context manager.
        pytest.raises(ValueError, int, "asdf").match("invalid literal")
        with pytest.raises(AssertionError) as excinfo:
            pytest.raises(ValueError, int, "asdf").match(msg)
        assert str(excinfo.value) == expr

        pytest.raises(TypeError, int, match="invalid")

        def tfunc(match):
            raise ValueError(f"match={match}")

        pytest.raises(ValueError, tfunc, match="asdf").match("match=asdf")
        pytest.raises(ValueError, tfunc, match="").match("match=")

    def test_match_failure_string_quoting(self):
        with pytest.raises(AssertionError) as excinfo:
            with pytest.raises(AssertionError, match="'foo"):
                raise AssertionError("'bar")
        (msg,) = excinfo.value.args
        assert msg == 'Regex pattern "\'foo" does not match "\'bar".'

    def test_match_failure_exact_string_message(self):
        message = "Oh here is a message with (42) numbers in parameters"
        with pytest.raises(AssertionError) as excinfo:
            with pytest.raises(AssertionError, match=message):
                raise AssertionError(message)
        (msg,) = excinfo.value.args
        assert msg == (
            "Regex pattern 'Oh here is a message with (42) numbers in "
            "parameters' does not match 'Oh here is a message with (42) "
            "numbers in parameters'. Did you mean to `re.escape()` the regex?"
        )

    def test_raises_match_wrong_type(self):
        """Raising an exception with the wrong type and match= given.

        pytest should throw the unexpected exception - the pattern match is not
        really relevant if we got a different exception.
        """
        with pytest.raises(ValueError):
            with pytest.raises(IndexError, match="nomatch"):
                int("asdf")

    def test_raises_exception_looks_iterable(self):
        """
        Tests if a function raises a specific exception when it should. The function creates a custom exception class using a metaclass that raises a ZeroDivisionError when accessed as an iterable. The test expects the `pytest.raises` context manager to fail because the custom exception class looks like an iterable, leading to unexpected behavior.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        Failed: If the `pytest.raises` context manager does not raise the expected exception.
        
        Key Points:
        - A metaclass is
        """

        class Meta(type):
            def __getitem__(self, item):
                return 1 / 0

            def __len__(self):
                return 1

        class ClassLooksIterableException(Exception, metaclass=Meta):
            pass

        with pytest.raises(
            Failed,
            match=r"DID NOT RAISE <class 'raises(\..*)*ClassLooksIterableException'>",
        ):
            pytest.raises(ClassLooksIterableException, lambda: None)

    def test_raises_with_raising_dunder_class(self) -> None:
        """Test current behavior with regard to exceptions via __class__ (#4284)."""

        class CrappyClass(Exception):
            # Type ignored because it's bypassed intentionally.
            @property  # type: ignore
            def __class__(self):
                assert False, "via __class__"

        with pytest.raises(AssertionError) as excinfo:
            with pytest.raises(CrappyClass()):  # type: ignore[call-overload]
                pass
        assert "via __class__" in excinfo.value.args[0]

    def test_raises_context_manager_with_kwargs(self):
        with pytest.raises(TypeError) as excinfo:
            with pytest.raises(Exception, foo="bar"):  # type: ignore[call-overload]
                pass
        assert "Unexpected keyword arguments" in str(excinfo.value)

    def test_expected_exception_is_not_a_baseexception(self) -> None:
        """
        Test that the expected exception is not a BaseException.
        
        This function checks that the provided exception is a valid BaseException type. It raises a TypeError if the provided exception is not a valid BaseException type. The function tests three scenarios:
        1. A string is provided as the exception.
        2. A custom class `NotAnException` is provided as the exception.
        3. A tuple containing a string and a custom class `NotAnException` is provided as the exception.
        
        Parameters:
        None
        """

        with pytest.raises(TypeError) as excinfo:
            with pytest.raises("hello"):  # type: ignore[call-overload]
                pass  # pragma: no cover
        assert "must be a BaseException type, not str" in str(excinfo.value)

        class NotAnException:
            pass

        with pytest.raises(TypeError) as excinfo:
            with pytest.raises(NotAnException):  # type: ignore[type-var]
                pass  # pragma: no cover
        assert "must be a BaseException type, not NotAnException" in str(excinfo.value)

        with pytest.raises(TypeError) as excinfo:
            with pytest.raises(("hello", NotAnException)):  # type: ignore[arg-type]
                pass  # pragma: no cover
        assert "must be a BaseException type, not str" in str(excinfo.value)
