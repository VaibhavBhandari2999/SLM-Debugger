from django.test import SimpleTestCase
from django.utils.hashable import make_hashable


class TestHashable(SimpleTestCase):
    def test_equal(self):
        """
        Tests the `make_hashable` function to ensure it correctly converts various types of input into a hashable form.
        
        Parameters:
        - value: The input value to be converted. Can be a list, tuple, set, dictionary, or a nested combination of these types.
        
        Returns:
        - A hashable representation of the input value. The function aims to convert non-hashable structures (like lists and dictionaries) into hashable forms (like tuples and frozensets).
        
        Test Cases:
        - Empty list and
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
        class Unhashable:
            __hash__ = None

        with self.assertRaisesMessage(TypeError, "unhashable type: 'Unhashable'"):
            make_hashable(Unhashable())
))
