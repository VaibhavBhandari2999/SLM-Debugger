from datetime import datetime

from django.db.models import Value
from django.db.models.fields import DateTimeField
from django.db.models.lookups import YearLookup
from django.test import SimpleTestCase


class YearLookupTests(SimpleTestCase):
    def test_get_bound_params(self):
        """
        Tests the `get_bound_params` method of a `YearLookup` subclass.
        
        This method is expected to raise a `NotImplementedError` with a specific message
        when called. The `YearLookup` subclass being tested should implement this method
        to provide year-based filtering logic.
        
        Args:
        lhs (datetime): The left-hand side value for the lookup.
        rhs (datetime): The right-hand side value for the lookup.
        
        Raises:
        NotImplementedError: If the `get
        """

        look_up = YearLookup(
            lhs=Value(datetime(2010, 1, 1, 0, 0, 0), output_field=DateTimeField()),
            rhs=Value(datetime(2010, 1, 1, 23, 59, 59), output_field=DateTimeField()),
        )
        msg = 'subclasses of YearLookup must provide a get_bound_params() method'
        with self.assertRaisesMessage(NotImplementedError, msg):
            look_up.get_bound_params(datetime(2010, 1, 1, 0, 0, 0), datetime(2010, 1, 1, 23, 59, 59))
