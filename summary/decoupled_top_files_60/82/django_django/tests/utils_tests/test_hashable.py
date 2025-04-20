from django.test import SimpleTestCase
from django.utils.hashable import make_hashable


class TestHashable(SimpleTestCase):
    def test_equal(self):
        """
        Tests the `make_hashable` function with various input types to ensure it converts them to a hashable format.
        
        Parameters:
        - value (any): The input value to be tested. Can be a list, tuple, set, dictionary, or a nested combination of these.
        
        Returns:
        - tuple: The expected hashable representation of the input value.
        
        Test Cases:
        - Empty list and tuple should return an empty tuple.
        - A list with a string and an integer should return a tuple with the same
        """

        tests = (
            ([], ()),
            (['a', 1], ('a', 1)),
            ({}, ()),
            ({'a'}, ('a',)),
            (frozenset({'a'}), {'a'}),
            ({'a': 1, 'b': 2}, (('a', 1), ('b', 2))),
            ({'b': 2, 'a': 1}, (('a', 1), ('b', 2))),
            (('a', ['b', 1]), ('a', ('b', 1))),
            (('a', {'b': 1}), ('a', (('b', 1),))),
        )
        for value, expected in tests:
            with self.subTest(value=value):
                self.assertEqual(make_hashable(value), expected)

    def test_count_equal(self):
        tests = (
            ({'a': 1, 'b': ['a', 1]}, (('a', 1), ('b', ('a', 1)))),
            ({'a': 1, 'b': ('a', [1, 2])}, (('a', 1), ('b', ('a', (1, 2))))),
        )
        for value, expected in tests:
            with self.subTest(value=value):
                self.assertCountEqual(make_hashable(value), expected)

    def test_unhashable(self):
        """
        Test that an unhashable type raises a TypeError.
        
        This function checks if an instance of an unhashable class raises a TypeError
        when passed to the make_hashable function. The unhashable class 'Unhashable'
        is defined within the function and has a `__hash__` method set to None.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: If an instance of the unhashable class does not raise a TypeError.
        
        Usage:
        This function is
        """

        class Unhashable:
            __hash__ = None

        with self.assertRaisesMessage(TypeError, "unhashable type: 'Unhashable'"):
            make_hashable(Unhashable())
