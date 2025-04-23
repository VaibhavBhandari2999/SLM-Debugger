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
        class A:
            def __call__(self):
                pass

        try:
            pytest.raises(ValueError, A())
        except pytest.raises.Exception:
            pass

    def test_raises_falsey_type_error(self):
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
        Tests the `test_division` function using parametrized inputs and expectations.
        
        Parameters:
        - testdir (pytest.Testdir): A pytest test directory object used to create and run test files.
        
        Key Parameters:
        - `example_input`: The input value for the division operation.
        - `expectation`: The expected outcome, either `does_not_raise()` or `pytest.raises(ZeroDivisionError)`.
        
        The function creates a test file with parametrized test cases for the `test_division` function
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
        with pytest.raises(TypeError, match="unknown"):
            with pytest.raises(TypeError, unknown="bogus"):
                raise ValueError()

    def test_tuple(self):
        with pytest.raises((KeyError, ValueError)):
            raise KeyError("oops")

    def test_no_raise_message(self):
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
        Tests for the `test_raises_match` function.
        
        This function tests various scenarios for raising exceptions and matching error messages using pytest's `raises` context manager. It checks for specific error messages and patterns, and also tests the use of the `match` parameter outside of the context manager.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Scenarios:
        1. Raises `ValueError` with a specific message pattern.
        2. Raises `ValueError` with a specific base.
        3. Raises `
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
        Tests the behavior of pytest.raises context manager with unexpected keyword arguments.
        
        This function checks that pytest.raises raises a TypeError when unexpected keyword arguments are provided to the context manager.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: If unexpected keyword arguments are provided to pytest.raises.
        
        Key Points:
        - The function uses pytest.raises as a context manager.
        - It attempts to use pytest.raises with a keyword argument 'foo' which is unexpected.
        - It asserts that the error message contains the phrase
        """

        with pytest.raises(TypeError) as excinfo:
            with pytest.raises(Exception, foo="bar"):
                pass
        assert "Unexpected keyword arguments" in str(excinfo.value)
assert "Unexpected keyword arguments" in str(excinfo.value)
