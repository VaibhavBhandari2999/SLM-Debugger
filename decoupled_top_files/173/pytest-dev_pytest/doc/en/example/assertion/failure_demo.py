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
        """
        Asserts that the function `f` returns the same value as the function `g`. Both functions do not take any arguments and return integer values.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - f: Returns 42
        - g: Returns 43
        
        Raises:
        AssertionError: If the return values of `f` and `g` are not equal.
        """

        def f():
            return 42

        def g():
            return 43

        assert f() == g()

    def test_simple_multiline(self):
        otherfunc_multi(42, 6 * 9)

    def test_not(self):
        """
        Tests if the result of calling function `f` is `False`. The function `f` returns an integer value, but the `not` operator is applied to its result, so the assertion will pass only if `f()` returns `0` or an empty value.
        """

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
        """
        Test if two long strings, `a` and `b`, are equal. Both strings consist of 100 '1's, followed by a different character ('a' or 'b'), and then 100 '2's. The assertion checks if these strings are equal, which should fail due to the differing characters.
        
        Args:
        None (the function creates its own variables `a` and `b`)
        
        Returns:
        AssertionError: If the strings `a`
        """

        a = "1" * 100 + "a" + "2" * 100
        b = "1" * 100 + "b" + "2" * 100
        assert a == b

    def test_eq_long_text_multiline(self):
        """
        Test if two long multiline strings are equal.
        
        Args:
        None (The function uses hardcoded string variables `a` and `b`).
        
        Returns:
        AssertionError: If the two strings are not equal.
        
        Variables:
        a (str): A long multiline string consisting of '1' repeated 100 times, followed by 'a', and then '2' repeated 100 times.
        b (str): A similar long multiline string but with 'b' instead
        """

        a = "1\n" * 100 + "a" + "2\n" * 100
        b = "1\n" * 100 + "b" + "2\n" * 100
        assert a == b

    def test_eq_list(self):
        assert [0, 1, 2] == [0, 1, 3]

    def test_eq_list_long(self):
        """
        Asserts that two lists, `a` and `b`, are not equal. Both lists are created by concatenating three sequences:
        - 100 zeros (`[0] * 100`)
        - A single element (either 1 or 2)
        - 100 threes (`[3] * 100`)
        
        The function generates these lists with different elements at the second position (1 vs. 2) and asserts their
        """

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
        Tests the equality of two instances of a dataclass.
        
        This function creates two instances of the `Foo` dataclass with different values for the 'b' attribute. It then asserts that these two instances are not equal.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `@dataclass`: A decorator from the `dataclasses` module used to define a dataclass.
        - `Foo`: A dataclass with attributes `a` (int)
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
        """
        Tests equality of two instances of the `Foo` class created using the `attr` library.
        
        Args:
        None (The function uses predefined instances of `Foo` class)
        
        Returns:
        bool: True if the instances are equal based on their attributes, False otherwise.
        
        Attributes:
        left (Foo): An instance of the `Foo` class with attributes `a=1` and `b='b'`.
        right (Foo): An instance of the `Foo` class with
        """

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
    Test the attribute of an instance of the class 'Foo'. The class 'Foo' has an attribute 'b' with an initial value of 1. The function creates an instance 'i' of the class 'Foo', modifies the attribute 'b' to 2, and asserts that the modified attribute value is equal to 2.
    """

    class Foo:
        b = 1

    i = Foo()
    assert i.b == 2


def test_attribute_instance():
    """
    Test the attribute of an instance of the class 'Foo'. The class 'Foo' has a class attribute 'b' initialized to 1. The function modifies the value of 'b' to 2 and asserts that the instance of 'Foo' returns the updated value of 'b'.
    """

    class Foo:
        b = 1

    assert Foo().b == 2


def test_attribute_failure():
    """
    Test attribute failure with a custom property getter that raises an exception.
    
    This function creates a class `Foo` with a custom property `b` that uses a
    getter method `_get_b`. The getter method is designed to raise an exception,
    simulating a failure when trying to access the attribute. The function then
    attempts to assert that the value of `i.b` is equal to 2, which will fail due
    to the raised exception.
    
    Args:
    None
    """

    class Foo:
        def _get_b(self):
            raise Exception("Failed to get attrib")

        b = property(_get_b)

    i = Foo()
    assert i.b == 2


def test_attribute_multiple():
    """
    Test the equality of attribute 'b' between instances of classes Foo and Bar.
    
    Args:
    None
    
    Returns:
    bool: True if the attribute 'b' is equal in both instances, False otherwise.
    
    Classes:
    Foo: A class with an attribute 'b' set to 1.
    Bar: A class with an attribute 'b' set to 2.
    
    Attributes:
    b (int): An integer attribute of the classes Foo and Bar.
    """

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
        raises(IOError, int, "3")

    def test_raise(self):
        raise ValueError("demo error")

    def test_tupleerror(self):
        a, b = [1]  # NOQA

    def test_reinterpret_fails_with_print_for_the_fun_of_it(self):
        """
        Test that reinterpreting fails with a print statement for demonstration purposes.
        
        Args:
        self: The instance of the class containing this method.
        
        Summary:
        This function takes a list `items` as input and prints its contents. It then attempts to unpack the list using the `pop()` method, which modifies the original list by removing and returning the last element. The function does not return any value.
        
        Variables:
        items (list): A list containing integer values [1,
        """

        items = [1, 2, 3]
        print("items is %r" % items)
        a, b = items.pop()

    def test_some_error(self):
        if namenotexi:  # NOQA
            pass

    def func1(self):
        assert 41 == 42


# thanks to Matthew Scott for this test
def test_dynamic_compile_shows_nicely():
    """
    Compile and execute dynamic code with the given source, module name, and function name.
    
    This function takes a string of Python code, compiles it into an executable code object,
    and then executes it within a new module. The compiled code is stored in the `sys.modules`
    dictionary under the specified module name. The function then calls the specified function
    from the module, which in this case is 'foo'.
    
    Args:
    src (str): The source code to be compiled
    """

    import imp
    import sys

    src = "def foo():\n assert 1 == 0\n"
    name = "abc-123"
    module = imp.new_module(name)
    code = _pytest._code.compile(src, name, "exec")
    exec(code, module.__dict__)
    sys.modules[name] = module
    module.foo()


class TestMoreErrors:
    def test_complex_error(self):
        """
        Tests a complex error scenario involving two functions, `f` and `g`, which return integers 44 and 43 respectively. The `somefunc` function is called with the results of `f()` and `g()` as arguments.
        
        Args:
        None (The function does not accept any explicit arguments).
        
        Returns:
        None (The function does not return anything explicitly).
        
        Functions Used:
        - `f`: Returns the integer 44.
        - `g`:
        """

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
        """
        Tests if the string `s` starts with the substring `g`.
        
        Args:
        s (str): The input string.
        g (str): The substring to check against.
        
        Returns:
        bool: True if `s` starts with `g`, False otherwise.
        
        Raises:
        None
        
        Example:
        >>> test_startswith("123", "456")
        False
        """

        s = "123"
        g = "456"
        assert s.startswith(g)

    def test_startswith_nested(self):
        """
        Asserts that the result of calling `f()` starts with the result of calling `g()`.
        
        The function `f()` returns the string '123', while `g()` returns the string '456'. The `startswith` method is used to check if the string returned by `f()` begins with the string returned by `g()`, which is expected to be False in this case.
        
        Args:
        None
        
        Returns:
        None
        """

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
        Test a try-finally block.
        
        This function attempts to assert that `x` is equal to 0, which will fail since `x` is initially set to 1. The finally block ensures that `x` is set to 0 regardless of whether the assertion succeeds or fails.
        
        Args:
        None
        
        Returns:
        None
        """

        x = 1
        try:
            assert x == 0
        finally:
            x = 0


class TestCustomAssertMsg:
    def test_single_line(self):
        """
        Test that the value of `A.a` is equal to `b`.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If `A.a` is not equal to `b`.
        
        Variables:
        A (class): A class with an attribute `a`.
        b (int): An integer value.
        
        Important Functions:
        - `assert`: Used to verify that `A.a` is equal to `b`. If not, an AssertionError is raised
        """

        class A:
            a = 1

        b = 2
        assert A.a == b, "A.a appears not to be b"

    def test_multiline(self):
        """
        Tests if the attribute 'a' of class A is equal to the variable 'b'. If not, an assertion error is raised with a multi-line message indicating the discrepancy.
        """

        class A:
            a = 1

        b = 2
        assert (
            A.a == b
        ), "A.a appears not to be b\nor does not appear to be b\none of those"

    def test_custom_repr(self):
        """
        Test custom representation of a JSON-like object.
        
        This test checks if the custom `__repr__` method defined in the `JSON` class
        correctly returns a specific string representation. The `assert` statement
        compares the attribute `a` of an instance of the `JSON` class with the
        integer `b`, and prints the instance's representation if the assertion fails.
        
        Args:
        None (The test function does not take any arguments).
        
        Returns:
        None (
        """

        class JSON:
            a = 1

            def __repr__(self):
                return "This is JSON\n{\n  'foo': 'bar'\n}"

        a = JSON()
        b = 2
        assert a.a == b, a
