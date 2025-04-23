import unittest

from django.db import connection
from django.test import TestCase


@unittest.skipUnless(connection.vendor == 'mysql', 'MySQL tests')
class SchemaEditorTests(TestCase):
    def test_quote_value(self):
        """
        Tests the `quote_value` method of the schema editor.
        
        This function tests the `quote_value` method of the schema editor against various input values to ensure that the method correctly formats and quotes the values for SQL insertion. The method is expected to handle strings, integers, floats, and boolean values.
        
        Parameters:
        - value: The value to be quoted and formatted for SQL insertion.
        - expected: The expected quoted and formatted string representation of the value.
        
        Returns:
        - None: The function asserts that the
        """

        import MySQLdb
        editor = connection.schema_editor()
        tested_values = [
            ('string', "'string'"),
            (42, '42'),
            (1.754, '1.754e0' if MySQLdb.version_info >= (1, 3, 14) else '1.754'),
            (False, b'0' if MySQLdb.version_info >= (1, 4, 0) else '0'),
        ]
        for value, expected in tested_values:
            with self.subTest(value=value):
                self.assertEqual(editor.quote_value(value), expected)
