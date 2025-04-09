import re
import sys

import pytest
from _pytest.outcomes import Failed


class TestRaises:
    def test_check_callable(self):
        with pytest.raises(TypeError, match=r".* must be callable"):
            pytest.raises(RuntimeError, "int('qwe')")

    def test_raises(self):
        excinfo = pytest.raises(ValueError, int, "qwe")
        assert "invalid literal" in str(excinfo.value)

    def test_raises_function(self):
        excinfo = pytest.raises(ValueError, int, "hello")
        assert "invalid literal" in str(excinfo.value)

    def test_raises_callable_no_exception(self):
        """
        Tests if a callable object raises a specific exception.
        
        This function checks whether an instance of the `A` class, which is a callable object, raises a `ValueError`. The `pytest.raises` context manager is used to assert that the callable does not raise any exception. If an exception is raised, it is caught and ignored.
        
        Args:
        None (This function does not take any input arguments).
        
        Returns:
        None (This function does not return any value).
        
        Raises:
        """

        class A:
            def __call__(self):
                pass

        try:
            pytest.raises(ValueError, A())
        except pytest.raises.Exception:
            pass

    def test_raises_falsey_type_error(self):
        """
        Raises a TypeError if an AssertionError is not raised with the specified message.
        
        This function attempts to raise an AssertionError with the given message
        inside a nested pytest.raises block. If the AssertionError is not raised,
        a TypeError is raised.
        
        Args:
        None
        
        Raises:
        TypeError: If the inner pytest.raises block does not raise an AssertionError.
        """

        with pytest.raises(TypeError):
            with pytest.raises(AssertionError, match=0):
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

    def test_raises_as_contextmanager(self, testdir):
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

        testdir.makepyfile(
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
        result = testdir.runpytest()
        result.stdout.fnmatch_lines(["*3 passed*"])

    def test_does_not_raise(self, testdir):
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

        testdir.makepyfile(
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
        result = testdir.runpytest()
        result.stdout.fnmatch_lines(["*4 passed*"])

    def test_does_not_raise_does_raise(self, testdir):
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

        testdir.makepyfile(
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
        result = testdir.runpytest()
        result.stdout.fnmatch_lines(["*2 failed*"])

    def test_noclass(self):
        with pytest.raises(TypeError):
            pytest.raises("wrong", lambda: None)

    def test_invalid_arguments_to_raises(self):
        """
        Test invalid arguments passed to `pytest.raises`.
        
        This function checks that passing an invalid argument (`unknown`) to
        `pytest.raises` raises a `TypeError` with a specific message.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: If an invalid argument is passed to `pytest.raises`.
        
        Usage:
        >>> test_invalid_arguments_to_raises()
        """

        with pytest.raises(TypeError, match="unknown"):
            with pytest.raises(TypeError, unknown="bogus"):
                raise ValueError()

    def test_tuple(self):
        with pytest.raises((KeyError, ValueError)):
            raise KeyError("oops")

    def test_no_raise_message(self):
        """
        Tests that the `pytest.raises` context manager is used correctly to check if an exception is raised.
        
        This function checks two scenarios:
        1. Verifies that the `int("0")` call does not raise a `ValueError`.
        2. Verifies that the `with pytest.raises(ValueError): pass` block does not raise a `ValueError`.
        
        In both cases, if the expected exception is not raised, a `pytest.raises.Exception` is caught and an assertion is
        """

        try:
            pytest.raises(ValueError, int, "0")
        except pytest.raises.Exception as e:
            assert e.msg == "DID NOT RAISE {}".format(repr(ValueError))
        else:
            assert False, "Expected pytest.raises.Exception"

        try:
            with pytest.raises(ValueError):
                pass
        except pytest.raises.Exception as e:
            assert e.msg == "DID NOT RAISE {}".format(repr(ValueError))
        else:
            assert False, "Expected pytest.raises.Exception"

    @pytest.mark.parametrize("method", ["function", "function_match", "with"])
    def test_raises_cyclic_reference(self, method):
        """
        Ensure pytest.raises does not leave a reference cycle (#1965).
        """
        import gc

        class T:
            def __call__(self):
                """
                __call__(self)
                
                Raises a ValueError. This method is called when an instance of the class is called as a function. In earlier versions of Python 3.5, this method may leave a reference to 't' in the frame, which this code mitigates by deleting 'self'. The function does not accept any parameters and does not return any value.
                """

                # Early versions of Python 3.5 have some bug causing the
                # __call__ frame to still refer to t even after everything
                # is done. This makes the test pass for them.
                if sys.version_info < (3, 5, 2):
                    del self
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
        
        This function tests different ways of raising exceptions and matching error messages using pytest's `pytest.raises` context manager. It includes tests for:
        - Raising a ValueError with a specific message pattern.
        - Using the `match` parameter directly within the `pytest.raises` context manager.
        - Matching a custom error message pattern.
        - Testing for a TypeError when no exception is raised.
        - Matching a custom message to a function that
        """

        msg = r"with base \d+"
        with pytest.raises(ValueError, match=msg):
            int("asdf")

        msg = "with base 10"
        with pytest.raises(ValueError, match=msg):
            int("asdf")

        msg = "with base 16"
        expr = "Pattern {!r} does not match \"invalid literal for int() with base 10: 'asdf'\"".format(
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
            raise ValueError("match={}".format(match))

        pytest.raises(ValueError, tfunc, match="asdf").match("match=asdf")
        pytest.raises(ValueError, tfunc, match="").match("match=")

    def test_match_failure_string_quoting(self):
        """
        Test that an `AssertionError` is raised when the expected match pattern does not match the actual error message.
        
        This test checks that the `pytest.raises` context manager correctly handles string quoting and matching. It raises an `AssertionError` with a specific message and attempts to match the pattern `'foo'` against the message `'bar'`. The test asserts that the exception message indicates that the pattern does not match the actual message.
        
        Args:
        None
        
        Returns:
        None
        """

        with pytest.raises(AssertionError) as excinfo:
            with pytest.raises(AssertionError, match="'foo"):
                raise AssertionError("'bar")
        (msg,) = excinfo.value.args
        assert msg == 'Pattern "\'foo" does not match "\'bar"'

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

    def test_raises_with_raising_dunder_class(self):
        """Test current behavior with regard to exceptions via __class__ (#4284)."""

        class CrappyClass(Exception):
            # Type ignored because it's bypassed intentionally.
            @property  # type: ignore
            def __class__(self):
                assert False, "via __class__"

        with pytest.raises(AssertionError) as excinfo:
            with pytest.raises(CrappyClass()):
                pass
        assert "via __class__" in excinfo.value.args[0]

    def test_raises_context_manager_with_kwargs(self):
        """
        Tests that a TypeError is raised when using unexpected keyword arguments in a context manager.
        
        Summary:
        - Function: `test_raises_context_manager_with_kwargs`
        - Uses: `pytest.raises` context manager
        - Raises: `TypeError`
        - Checks for: "Unexpected keyword arguments" in the error message
        
        Args:
        - No explicit input arguments
        
        Returns:
        - No explicit return value
        
        Example:
        >>> test_raises_context_manager_with_kwargs()
        """

        with pytest.raises(TypeError) as excinfo:
            with pytest.raises(Exception, foo="bar"):
                pass
        assert "Unexpected keyword arguments" in str(excinfo.value)
