from datetime import datetime
from unittest import mock

from django.db.models import DateTimeField, Value
from django.db.models.lookups import Lookup, YearLookup
from django.test import SimpleTestCase


class CustomLookup(Lookup):
    pass


class LookupTests(SimpleTestCase):
    def test_equality(self):
        lookup = Lookup(Value(1), Value(2))
        self.assertEqual(lookup, lookup)
        self.assertEqual(lookup, Lookup(lookup.lhs, lookup.rhs))
        self.assertEqual(lookup, mock.ANY)
        self.assertNotEqual(lookup, Lookup(lookup.lhs, Value(3)))
        self.assertNotEqual(lookup, Lookup(Value(3), lookup.rhs))
        self.assertNotEqual(lookup, CustomLookup(lookup.lhs, lookup.rhs))

    def test_repr(self):
        """
        Test the `repr` method for different types of lookups.
        
        This function tests the `repr` method for various lookup objects, including a simple `Lookup` and a `YearLookup`. The `Lookup` object is initialized with a value and a key, while the `YearLookup` is initialized with a start and end datetime for the year lookup. The expected `repr` output is provided for each test case.
        
        Parameters:
        - lookup (object): The lookup object to test.
        - expected (
        """

        tests = [
            (Lookup(Value(1), Value("a")), "Lookup(Value(1), Value('a'))"),
            (
                YearLookup(
                    Value(datetime(2010, 1, 1, 0, 0, 0)),
                    Value(datetime(2010, 1, 1, 23, 59, 59)),
                ),
                "YearLookup("
                "Value(datetime.datetime(2010, 1, 1, 0, 0)), "
                "Value(datetime.datetime(2010, 1, 1, 23, 59, 59)))",
            ),
        ]
        for lookup, expected in tests:
            with self.subTest(lookup=lookup):
                self.assertEqual(repr(lookup), expected)

    def test_hash(self):
        lookup = Lookup(Value(1), Value(2))
        self.assertEqual(hash(lookup), hash(lookup))
        self.assertEqual(hash(lookup), hash(Lookup(lookup.lhs, lookup.rhs)))
        self.assertNotEqual(hash(lookup), hash(Lookup(lookup.lhs, Value(3))))
        self.assertNotEqual(hash(lookup), hash(Lookup(Value(3), lookup.rhs)))
        self.assertNotEqual(hash(lookup), hash(CustomLookup(lookup.lhs, lookup.rhs)))


class YearLookupTests(SimpleTestCase):
    def test_get_bound_params(self):
        """
        Tests the `get_bound_params` method for subclasses of `YearLookup`.
        
        This method is expected to raise a `NotImplementedError` with a specific message
        if it is not overridden in a subclass.
        
        Parameters:
        lhs (datetime): The left-hand side datetime value.
        rhs (datetime): The right-hand side datetime value.
        
        Raises:
        NotImplementedError: If the method is not implemented in a subclass.
        The error message will be "subclasses of YearLookup must provide a get_bound_params
        """

        look_up = YearLookup(
            lhs=Value(datetime(2010, 1, 1, 0, 0, 0), output_field=DateTimeField()),
            rhs=Value(datetime(2010, 1, 1, 23, 59, 59), output_field=DateTimeField()),
        )
        msg = "subclasses of YearLookup must provide a get_bound_params() method"
        with self.assertRaisesMessage(NotImplementedError, msg):
            look_up.get_bound_params(
                datetime(2010, 1, 1, 0, 0, 0), datetime(2010, 1, 1, 23, 59, 59)
            )
