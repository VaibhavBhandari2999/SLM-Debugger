import _pytest._code
import pytest
from pytest import raises


def otherfunc(a, b):
    assert a == b


def somefunc(x, y):
    otherfunc(x, y)


def otherfunc_multi(a, b):
    assert a == b


@pytest.mark.parametrize("param1, param2", [(3, 6)])
def test_generative(param1, param2):
    assert param1 * 2 < param2


class TestFailing:
    def test_simple(self):
        def f():
            return 42

        def g():
            return 43

        assert f() == g()

    def test_simple_multiline(self):
        otherfunc_multi(42, 6 * 9)

    def test_not(self):
        def f():
            return 42

        assert not f()


class TestSpecialisedExplanations:
    def test_eq_text(self):
        assert "spam" == "eggs"

    def test_eq_similar_text(self):
        assert "foo 1 bar" == "foo 2 bar"

    def test_eq_multiline_text(self):
        assert "foo\nspam\nbar" == "foo\neggs\nbar"

    def test_eq_long_text(self):
        a = "1" * 100 + "a" + "2" * 100
        b = "1" * 100 + "b" + "2" * 100
        assert a == b

    def test_eq_long_text_multiline(self):
        a = "1\n" * 100 + "a" + "2\n" * 100
        b = "1\n" * 100 + "b" + "2\n" * 100
        assert a == b

    def test_eq_list(self):
        assert [0, 1, 2] == [0, 1, 3]

    def test_eq_list_long(self):
        a = [0] * 100 + [1] + [3] * 100
        b = [0] * 100 + [2] + [3] * 100
        assert a == b

    def test_eq_dict(self):
        assert {"a": 0, "b": 1, "c": 0} == {"a": 0, "b": 2, "d": 0}

    def test_eq_set(self):
        assert {0, 10, 11, 12} == {0, 20, 21}

    def test_eq_longer_list(self):
        assert [1, 2] == [1, 2, 3]

    def test_in_list(self):
        assert 1 in [0, 2, 3, 4, 5]

    def test_not_in_text_multiline(self):
        text = "some multiline\ntext\nwhich\nincludes foo\nand a\ntail"
        assert "foo" not in text

    def test_not_in_text_single(self):
        text = "single foo line"
        assert "foo" not in text

    def test_not_in_text_single_long(self):
        text = "head " * 50 + "foo " + "tail " * 20
        assert "foo" not in text

    def test_not_in_text_single_long_term(self):
        text = "head " * 50 + "f" * 70 + "tail " * 20
        assert "f" * 70 not in text

    def test_eq_dataclass(self):
        """
        Test equality of two instances of a dataclass.
        
        This function tests the equality of two instances of a dataclass named `Foo`. The `Foo` dataclass is defined with two fields: `a` of type `int` and `b` of type `str`.
        
        Parameters:
        None
        
        Returns:
        None
        
        Example:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class Foo:
        ...     a: int
        ...     b: str
        """

        from dataclasses import dataclass

        @dataclass
        class Foo:
            a: int
            b: str

        left = Foo(1, "b")
        right = Foo(1, "c")
        assert left == right

    def test_eq_attrs(self):
        import attr

        @attr.s
        class Foo:
            a = attr.ib()
            b = attr.ib()

        left = Foo(1, "b")
        right = Foo(1, "c")
        assert left == right


def test_attribute():
    """
    This function tests the attribute assignment in a class. It creates a class `Foo` with a class attribute `b` set to 1. An instance `i` of `Foo` is created, and the function asserts that the value of `i.b` is 2.
    
    No parameters or keywords are required for this function. It does not return any value; it only performs an assertion check.
    
    Note:
    - The function modifies the class attribute `b` of the instance `i` to
    """

    class Foo:
        b = 1

    i = Foo()
    assert i.b == 2


def test_attribute_instance():
    class Foo:
        b = 1

    assert Foo().b == 2


def test_attribute_failure():
    class Foo:
        def _get_b(self):
            raise Exception("Failed to get attrib")

        b = property(_get_b)

    i = Foo()
    assert i.b == 2


def test_attribute_multiple():
    class Foo:
        b = 1

    class Bar:
        b = 2

    assert Foo().b == Bar().b


def globf(x):
    return x + 1


class TestRaises:
    def test_raises(self):
        s = "qwe"
        raises(TypeError, int, s)

    def test_raises_doesnt(self):
        raises(OSError, int, "3")

    def test_raise(self):
        raise ValueError("demo error")

    def test_tupleerror(self):
        a, b = [1]  # NOQA

    def test_reinterpret_fails_with_print_for_the_fun_of_it(self):
        """
        Test that reinterpreting a list fails as expected.
        
        This function tests the behavior of reinterpreting a list. It pops an item from a list and attempts to unpack it into two variables, which should fail since a single item cannot be unpacked into two variables. The function prints the original list before the operation.
        
        Parameters:
        None
        
        Returns:
        None
        
        Side Effects:
        - Prints the original list.
        - Raises a ValueError due to attempting to unpack a single item into two variables
        """

        items = [1, 2, 3]
        print("items is {!r}".format(items))
        a, b = items.pop()

    def test_some_error(self):
        if namenotexi:  # NOQA
            pass

    def func1(self):
        assert 41 == 42


# thanks to Matthew Scott for this test
def test_dynamic_compile_shows_nicely():
    """
    Test dynamic compilation and execution of a Python function.
    
    This function demonstrates how to dynamically compile and execute a Python function using the `importlib.util` module. It takes a source code string and a module name as input, compiles the source code into a code object, and then executes it in a new module. If the compiled function contains an assertion that fails, the function will raise an AssertionError.
    
    Parameters:
    src (str): The source code of the function to be compiled and executed.
    """

    import importlib.util
    import sys

    src = "def foo():\n assert 1 == 0\n"
    name = "abc-123"
    spec = importlib.util.spec_from_loader(name, loader=None)
    module = importlib.util.module_from_spec(spec)
    code = _pytest._code.compile(src, name, "exec")
    exec(code, module.__dict__)
    sys.modules[name] = module
    module.foo()


class TestMoreErrors:
    def test_complex_error(self):
        def f():
            return 44

        def g():
            return 43

        somefunc(f(), g())

    def test_z1_unpack_error(self):
        items = []
        a, b = items

    def test_z2_type_error(self):
        items = 3
        a, b = items

    def test_startswith(self):
        s = "123"
        g = "456"
        assert s.startswith(g)

    def test_startswith_nested(self):
        def f():
            return "123"

        def g():
            return "456"

        assert f().startswith(g())

    def test_global_func(self):
        assert isinstance(globf(42), float)

    def test_instance(self):
        self.x = 6 * 7
        assert self.x != 42

    def test_compare(self):
        assert globf(10) < 5

    def test_try_finally(self):
        """
        Tests a try-finally block.
        
        This function tests the behavior of a try-finally block in Python. It sets the variable `x` to 1, then enters a try block where an assertion fails, causing an AssertionError to be raised. The finally block is executed regardless of whether an exception is raised in the try block. In the finally block, `x` is set to 0.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the value of `
        """

        x = 1
        try:
            assert x == 0
        finally:
            x = 0


class TestCustomAssertMsg:
    def test_single_line(self):
        class A:
            a = 1

        b = 2
        assert A.a == b, "A.a appears not to be b"

    def test_multiline(self):
        class A:
            a = 1

        b = 2
        assert (
            A.a == b
        ), "A.a appears not to be b\nor does not appear to be b\none of those"

    def test_custom_repr(self):
        class JSON:
            a = 1

            def __repr__(self):
                return "This is JSON\n{\n  'foo': 'bar'\n}"

        a = JSON()
        b = 2
        assert a.a == b, a
