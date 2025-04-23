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
        """
        Tests the hash functionality of the Lookup class.
        
        This function checks the hash behavior of the Lookup class instances. It ensures that:
        - Two identical Lookup instances have the same hash value.
        - A Lookup instance has the same hash value as another instance with the same operands.
        - A Lookup instance has a different hash value if one of its operands is different.
        - A Lookup instance has a different hash value if it is compared with an instance of a different class (CustomLookup) with the same operands.
        
        Parameters
        """

        lookup = Lookup(Value(1), Value(2))
        self.assertEqual(hash(lookup), hash(lookup))
        self.assertEqual(hash(lookup), hash(Lookup(lookup.lhs, lookup.rhs)))
        self.assertNotEqual(hash(lookup), hash(Lookup(lookup.lhs, Value(3))))
        self.assertNotEqual(hash(lookup), hash(Lookup(Value(3), lookup.rhs)))
        self.assertNotEqual(hash(lookup), hash(CustomLookup(lookup.lhs, lookup.rhs)))


class YearLookupTests(SimpleTestCase):
    def test_get_bound_params(self):
        look_up = YearLookup(
            lhs=Value(datetime(2010, 1, 1, 0, 0, 0), output_field=DateTimeField()),
            rhs=Value(datetime(2010, 1, 1, 23, 59, 59), output_field=DateTimeField()),
        )
        msg = "subclasses of YearLookup must provide a get_bound_params() method"
        with self.assertRaisesMessage(NotImplementedError, msg):
            look_up.get_bound_params(
                datetime(2010, 1, 1, 0, 0, 0), datetime(2010, 1, 1, 23, 59, 59)
            )
