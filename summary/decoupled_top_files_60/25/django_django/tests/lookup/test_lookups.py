from datetime import datetime

from django.db.models import Value
from django.db.models.fields import DateTimeField
from django.db.models.lookups import YearLookup
from django.test import SimpleTestCase


class YearLookupTests(SimpleTestCase):
    def test_get_bound_params(self):
        """
        Tests the `get_bound_params` method for subclasses of `YearLookup`.
        
        This method is expected to be implemented by subclasses to handle the
        bound parameters correctly. If not implemented, a `NotImplementedError`
        is raised with a specific message.
        
        Parameters:
        lhs (datetime): The left-hand side datetime value.
        rhs (datetime): The right-hand side datetime value.
        
        Raises:
        NotImplementedError: If the `get_bound_params` method is not implemented
        in the subclass. The error message
        """

        look_up = YearLookup(
            lhs=Value(datetime(2010, 1, 1, 0, 0, 0), output_field=DateTimeField()),
            rhs=Value(datetime(2010, 1, 1, 23, 59, 59), output_field=DateTimeField()),
        )
        msg = 'subclasses of YearLookup must provide a get_bound_params() method'
        with self.assertRaisesMessage(NotImplementedError, msg):
            look_up.get_bound_params(datetime(2010, 1, 1, 0, 0, 0), datetime(2010, 1, 1, 23, 59, 59))
