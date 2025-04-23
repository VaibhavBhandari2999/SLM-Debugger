from datetime import datetime
from unittest import mock

from django.db.models import DateTimeField, Value
from django.db.models.lookups import Lookup, YearLookup
from django.test import SimpleTestCase


class CustomLookup(Lookup):
    pass


class LookupTests(SimpleTestCase):
    def test_equality(self):
        """
        Test the equality of Lookup objects.
        
        This function tests the equality of Lookup objects. It compares a Lookup object with itself, with another Lookup object having the same values, with mock.ANY, and with different Lookup objects or a CustomLookup object.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - Lookup object is equal to itself.
        - Lookup object is equal to another Lookup object with the same values.
        - Lookup object is equal to mock.ANY.
        - Lookup object
        """

        lookup = Lookup(Value(1), Value(2))
        self.assertEqual(lookup, lookup)
        self.assertEqual(lookup, Lookup(lookup.lhs, lookup.rhs))
        self.assertEqual(lookup, mock.ANY)
        self.assertNotEqual(lookup, Lookup(lookup.lhs, Value(3)))
        self.assertNotEqual(lookup, Lookup(Value(3), lookup.rhs))
        self.assertNotEqual(lookup, CustomLookup(lookup.lhs, lookup.rhs))

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
        
        This method is expected to raise a `NotImplementedError` with a specific message.
        
        Parameters:
        lhs (datetime): The left-hand side datetime value.
        rhs (datetime): The right-hand side datetime value.
        
        Raises:
        NotImplementedError: If the subclass of `YearLookup` does not implement the `get_bound_params` method.
        The error message will be 'subclasses of YearLookup must provide a get_bound_params
        """

        look_up = YearLookup(
            lhs=Value(datetime(2010, 1, 1, 0, 0, 0), output_field=DateTimeField()),
            rhs=Value(datetime(2010, 1, 1, 23, 59, 59), output_field=DateTimeField()),
        )
        msg = 'subclasses of YearLookup must provide a get_bound_params() method'
        with self.assertRaisesMessage(NotImplementedError, msg):
            look_up.get_bound_params(datetime(2010, 1, 1, 0, 0, 0), datetime(2010, 1, 1, 23, 59, 59))
