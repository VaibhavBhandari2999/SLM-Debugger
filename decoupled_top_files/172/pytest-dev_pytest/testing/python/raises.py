import sys

import pytest
from _pytest.outcomes import Failed
from _pytest.warning_types import PytestDeprecationWarning


class TestRaises:
    def test_raises(self):
        """
        Tests that the given source code raises a ValueError.
        
        Args:
        self: The instance of the class containing this method.
        
        Raises:
        PytestDeprecationWarning: If the code does not raise a warning.
        
        Returns:
        None
        
        Notes:
        - The source code is expected to be a string representing a Python expression.
        - The function uses `pytest.raises` to capture the exception raised by the source code.
        - It checks if the exception is a ValueError.
        """

        source = "int('qwe')"
        with pytest.warns(PytestDeprecationWarning):
            excinfo = pytest.raises(ValueError, source)
        code = excinfo.traceback[-1].frame.code
        s = str(code.fullsource)
        assert s == source

    def test_raises_exec(self):
        """
        Test that raises an exception.
        
        This function tests whether a specific code snippet raises a `ValueError` exception. It uses the `pytest.raises` context manager to capture the raised exception and asserts that the warning is issued from the correct file using `pytest.warns`.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        PytestDeprecationWarning: If the warning is not issued from the correct file.
        
        Usage:
        >>> test_raises_exec()
        """

        with pytest.warns(PytestDeprecationWarning) as warninfo:
            pytest.raises(ValueError, "a,x = []")
        assert warninfo[0].filename == __file__

    def test_raises_exec_correct_filename(self):
        """
        Raises an exception and checks if the traceback contains the correct filename.
        
        This function tests whether an exception is raised correctly and if the traceback
        includes the expected filename. It uses `pytest.raises` to catch the exception and
        `pytest.warns` to handle deprecation warnings. The function asserts that the filename
        of the current file is present in the last traceback frame's path.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        PytestDeprec
        """

        with pytest.warns(PytestDeprecationWarning):
            excinfo = pytest.raises(ValueError, 'int("s")')
            assert __file__ in excinfo.traceback[-1].path

    def test_raises_syntax_error(self):
        """
        Test that raises a SyntaxError.
        
        This function tests whether a SyntaxError is raised when an invalid
        syntax is provided. It uses `pytest.raises` to capture the exception
        and `pytest.warns` to check for deprecation warnings. The test checks
        if the warning filename matches the current file.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        PytestDeprecationWarning: If the warning filename does not match the current file.
        """

        with pytest.warns(PytestDeprecationWarning) as warninfo:
            pytest.raises(SyntaxError, "qwe qwe qwe")
        assert warninfo[0].filename == __file__

    def test_raises_function(self):
        pytest.raises(ValueError, int, "hello")

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

    def test_custom_raise_message(self):
        """
        Test custom raise message.
        
        This function tests the custom raise message by using pytest.raises and pytest.warns to check if the expected warning and exception are raised with the specified message.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        PytestDeprecationWarning: If the deprecation warning is not raised.
        ValueError: If the value error is not raised with the specified message.
        
        Important Functions:
        - pytest.raises
        - pytest.warns
        """

        message = "TEST_MESSAGE"
        try:
            with pytest.warns(PytestDeprecationWarning):
                with pytest.raises(ValueError, message=message):
                    pass
        except pytest.raises.Exception as e:
            assert e.msg == message
        else:
            assert False, "Expected pytest.raises.Exception"

    @pytest.mark.parametrize("method", ["function", "with"])
    def test_raises_cyclic_reference(self, method):
        """
        Ensure pytest.raises does not leave a reference cycle (#1965).
        """
        import gc

        class T:
            def __call__(self):
                raise ValueError

        t = T()
        if method == "function":
            pytest.raises(ValueError, t)
        else:
            with pytest.raises(ValueError):
                t()

        # ensure both forms of pytest.raises don't leave exceptions in sys.exc_info()
        assert sys.exc_info() == (None, None, None)

        del t

        # ensure the t instance is not stuck in a cyclic reference
        for o in gc.get_objects():
            assert type(o) is not T

    def test_raises_match(self):
        """
        Tests for raising specific exceptions when converting strings to integers.
        
        - Raises `ValueError` with a message matching the regular expression `r"with base \d+"` when attempting to convert an invalid string to an integer without specifying a base.
        - Raises `ValueError` with a message exactly matching `"with base 10"` when attempting to convert an invalid string to an integer with base 10.
        - Raises `AssertionError` with a message containing the pattern `'Pattern '{}'
        """

        msg = r"with base \d+"
        with pytest.raises(ValueError, match=msg):
            int("asdf")

        msg = "with base 10"
        with pytest.raises(ValueError, match=msg):
            int("asdf")

        msg = "with base 16"
        expr = r"Pattern '{}' not found in 'invalid literal for int\(\) with base 10: 'asdf''".format(
            msg
        )
        with pytest.raises(AssertionError, match=expr):
            with pytest.raises(ValueError, match=msg):
                int("asdf", base=10)

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
        Tests if a function raises a specific exception when it should. The test uses a custom metaclass `Meta` that defines the behavior of the `__getitem__` and `__len__` methods to raise a ZeroDivisionError and indicate an iterable length of 1, respectively. It then creates a class `ClassLooksIterableException` using this metaclass, which inherits from `Exception`. The test expects `pytest.raises` to fail because the exception is not raised as expected, and it matches
        """

        class Meta(type(object)):
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
            @property
            def __class__(self):
                assert False, "via __class__"

        with pytest.raises(AssertionError) as excinfo:
            with pytest.raises(CrappyClass()):
                pass
        assert "via __class__" in excinfo.value.args[0]
