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
        Tests if a callable object raises a specific exception.
        
        This function checks whether an instance of the `A` class, which is a callable,
        raises a `ValueError`. If the callable does not raise the expected exception,
        a `pytest.fail.Exception` is caught and ignored.
        
        Args:
        None (This is a unit test function)
        
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
        """
        Raises a TypeError if an AssertionError is not raised with the expected message.
        
        This function tests whether an AssertionError is correctly raised with the
        expected message '0'. If an AssertionError is not raised or the message does
        not match '0', a TypeError is raised.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: If an AssertionError is not raised with the expected message.
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
        """
        Test invalid arguments passed to `pytest.raises`.
        
        This function checks that passing an invalid argument to `pytest.raises` raises a `TypeError` with the expected message.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: If an invalid argument is passed to `pytest.raises`.
        """

        with pytest.raises(TypeError, match="unknown"):
            with pytest.raises(TypeError, unknown="bogus"):  # type: ignore[call-overload]
                raise ValueError()

    def test_tuple(self):
        with pytest.raises((KeyError, ValueError)):
            raise KeyError("oops")

    def test_no_raise_message(self) -> None:
        """
        Tests that the `pytest.raises` context manager is used correctly to ensure that a specific exception is raised.
        
        This function checks that the `pytest.raises` context manager is used correctly to ensure that a `ValueError` is raised when attempting to convert a string to an integer using the `int` function. It also tests that the `with pytest.raises` syntax works as expected.
        
        Args:
        None
        
        Returns:
        None
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
        """
        Tests various scenarios for raising exceptions and matching error messages.
        
        - Tests raising `ValueError` with specific error messages using `pytest.raises`.
        - Verifies that the correct error message is matched when calling `int` with invalid input.
        - Checks that an `AssertionError` is raised when the expected error message does not match.
        - Demonstrates the use of `match` without a context manager.
        - Ensures that `TypeError` is raised when providing an invalid argument to `
        """

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
        """
        Test that an `AssertionError` is raised when the expected match fails.
        
        This function checks that an `AssertionError` is raised with a specific
        error message when the provided match pattern does not find a match in the
        exception message. The function uses `pytest.raises` to catch and inspect
        the `AssertionError`.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the match pattern does not find a match in the
        """

        with pytest.raises(AssertionError) as excinfo:
            with pytest.raises(AssertionError, match="'foo"):
                raise AssertionError("'bar")
        (msg,) = excinfo.value.args
        assert msg == 'Regex pattern "\'foo" does not match "\'bar".'

    def test_match_failure_exact_string_message(self):
        """
        Tests that an exact string message is matched when raising an AssertionError.
        
        Summary: This function tests the matching of an exact string message using regular expressions. It raises an AssertionError with a specific message and checks if the raised exception's message matches the expected one.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the raised exception's message does not match the expected one.
        
        Functions Used:
        - pytest.raises: Context manager for asserting exceptions.
        - re
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
        Tests if a function raises a specific exception that is iterable and causes a ZeroDivisionError.
        
        Summary:
        - Uses a custom metaclass `Meta` to define a class `ClassLooksIterableException` that behaves like an iterable but raises a ZeroDivisionError when accessed.
        - The `pytest.raises` function is used to check if the specified exception is raised.
        - The test expects the `pytest.raises` call to fail because the exception is iterable and causes a ZeroDivisionError.
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
        """
        Test that using unexpected keyword arguments in a context manager raises a TypeError.
        
        This test checks that when attempting to use unexpected keyword arguments (foo="bar") in a pytest.raises context manager, a TypeError is raised with the message indicating unexpected keyword arguments.
        """

        with pytest.raises(TypeError) as excinfo:
            with pytest.raises(Exception, foo="bar"):  # type: ignore[call-overload]
                pass
        assert "Unexpected keyword arguments" in str(excinfo.value)

    def test_expected_exception_is_not_a_baseexception(self) -> None:
        """
        Test that the expected exception is not a base exception.
        
        - Raises:
        TypeError: If the expected exception is not a subclass of BaseException.
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
