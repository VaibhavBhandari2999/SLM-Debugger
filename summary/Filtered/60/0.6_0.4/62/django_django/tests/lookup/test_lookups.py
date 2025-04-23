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
        Tests the equality of Lookup objects.
        
        This function checks the equality of Lookup objects, including comparisons with the original object, with a mock.ANY placeholder, and with different variations of the Lookup object. It also tests inequality with a different type of object.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Comparisons:
        - `lookup == lookup`: True
        - `lookup == Lookup(lookup.lhs, lookup.rhs)`: True
        - `lookup == mock.ANY`:
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
        Tests the get_bound_params method for YearLookup subclasses.
        
        This method is expected to raise a NotImplementedError with a specific message
        if the subclass does not implement the get_bound_params method.
        
        Parameters:
        lhs (datetime): The left-hand side datetime value.
        rhs (datetime): The right-hand side datetime value.
        
        Raises:
        NotImplementedError: If the subclass does not implement the get_bound_params method.
        The error message will be 'subclasses of YearLookup must provide a get_bound_params() method'.
        """

        look_up = YearLookup(
            lhs=Value(datetime(2010, 1, 1, 0, 0, 0), output_field=DateTimeField()),
            rhs=Value(datetime(2010, 1, 1, 23, 59, 59), output_field=DateTimeField()),
        )
        msg = 'subclasses of YearLookup must provide a get_bound_params() method'
        with self.assertRaisesMessage(NotImplementedError, msg):
            look_up.get_bound_params(datetime(2010, 1, 1, 0, 0, 0), datetime(2010, 1, 1, 23, 59, 59))
