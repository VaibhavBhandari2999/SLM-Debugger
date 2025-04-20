from django.db.backends.sqlite3._functions import (
    _sqlite_date_trunc,
    _sqlite_datetime_trunc,
    _sqlite_time_trunc,
)
from django.test import SimpleTestCase


class FunctionTests(SimpleTestCase):
    def test_sqlite_date_trunc(self):
        """
        Tests the `_sqlite_date_trunc` function for handling unsupported lookup types.
        
        This function attempts to perform a date truncation operation using SQLite with an unsupported lookup type and expects a ValueError to be raised.
        
        Parameters:
        - lookup (str): The lookup type for the date truncation operation.
        - date (str): The date string to be truncated.
        - arg1 (Any, optional): An optional argument, which is not used in this function.
        - arg2 (Any, optional
        """

        msg = "Unsupported lookup type: 'unknown-lookup'"
        with self.assertRaisesMessage(ValueError, msg):
            _sqlite_date_trunc("unknown-lookup", "2005-08-11", None, None)

    def test_sqlite_datetime_trunc(self):
        msg = "Unsupported lookup type: 'unknown-lookup'"
        with self.assertRaisesMessage(ValueError, msg):
            _sqlite_datetime_trunc("unknown-lookup", "2005-08-11 1:00:00", None, None)

    def test_sqlite_time_trunc(self):
        """
        Test the `_sqlite_time_trunc` function for SQLite time truncation.
        
        Args:
        lookup_type (str): The type of time truncation to perform. Supported types include 'year', 'quarter', 'month', 'week', 'day', 'hour', 'minute', and 'second'.
        value (str): The datetime string to be truncated, in the format 'YYYY-MM-DD HH:MM:SS'.
        tzinfo (Optional[tzinfo]): The timezone information to be used
        """

        msg = "Unsupported lookup type: 'unknown-lookup'"
        with self.assertRaisesMessage(ValueError, msg):
            _sqlite_time_trunc("unknown-lookup", "2005-08-11 1:00:00", None, None)
