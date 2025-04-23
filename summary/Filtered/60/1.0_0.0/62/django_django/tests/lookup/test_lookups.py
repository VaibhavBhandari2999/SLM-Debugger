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

    def test_hash(self):
        """
        Test the hash functionality of the Lookup class.
        
        This function tests the hash method of the Lookup class by comparing the hash values of different instances of the class.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The hash of a Lookup instance is equal to itself.
        - The hash of a Lookup instance is equal to the hash of an identical Lookup instance.
        - The hash of a Lookup instance is not equal to the hash of a different Lookup instance with a different right-hand side
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
        msg = 'subclasses of YearLookup must provide a get_bound_params() method'
        with self.assertRaisesMessage(NotImplementedError, msg):
            look_up.get_bound_params(datetime(2010, 1, 1, 0, 0, 0), datetime(2010, 1, 1, 23, 59, 59))
