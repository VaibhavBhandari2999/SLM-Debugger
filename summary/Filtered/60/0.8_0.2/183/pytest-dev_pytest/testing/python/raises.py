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
        Tests if a callable object raises a specific exception. The function takes no parameters and does not return anything. It defines a class `A` that is callable and does not raise any exceptions when called. The function then attempts to use `pytest.raises` to assert that an instance of `A` raises a `ValueError`. If `pytest.raises` fails, a `pytest.fail.Exception` is caught and the test passes.
        
        Key Points:
        - The function does not accept any parameters.
        - It does
        """

        class A:
            def __call__(self):
                pass

        try:
            pytest.raises(ValueError, A())
        except pytest.fail.Exception:
            pass

    def test_raises_falsey_type_error(self) -> None:
        """
        Tests that an `AssertionError` is raised with a specific message when attempting to raise it within a nested `pytest.raises` context manager.
        
        This function ensures that a `TypeError` is raised when an `AssertionError` is incorrectly raised with a non-boolean message inside a nested `pytest.raises` block.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: If the nested `pytest.raises` context manager is used incorrectly to raise an `AssertionError` with a non-
        """

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
        """
        Test function to verify that an `AssertionError` is raised with a specific message when using the `match` parameter.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the regex pattern does not match the expected message.
        
        Key Steps:
        1. Define the expected message as a string.
        2. Use a nested `with pytest.raises(AssertionError, match=message)` block to attempt raising an `AssertionError` with the specified message.
        3. Capture the raised
        """

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
        Test that an exception raised by a class that looks iterable raises a specific error message.
        
        This function tests the behavior of `pytest.raises` when the expected exception is a class that looks iterable but actually raises an exception when accessed. The class `ClassLooksIterableException` is defined with a metaclass `Meta` that overrides the `__getitem__` and `__len__` methods to simulate an iterable-like behavior that raises an exception.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
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
