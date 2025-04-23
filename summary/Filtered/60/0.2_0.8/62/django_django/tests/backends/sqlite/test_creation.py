import copy
import unittest

from django.db import DEFAULT_DB_ALIAS, connection, connections
from django.test import SimpleTestCase


@unittest.skipUnless(connection.vendor == 'sqlite', 'SQLite tests')
class TestDbSignatureTests(SimpleTestCase):
    def test_custom_test_name(self):
        """
        Function to test a custom database connection.
        
        This function creates a copy of the default database connection, modifies its settings to use a custom test database, and then generates a test database signature.
        
        Parameters:
        None
        
        Returns:
        tuple: A tuple containing two elements. The first element is the original database name (None in this case), and the second element is the custom test database name ('custom.sqlite.db').
        
        Usage:
        This function is typically used in testing scenarios where a custom test database needs
        """

        test_connection = copy.copy(connections[DEFAULT_DB_ALIAS])
        test_connection.settings_dict = copy.deepcopy(connections[DEFAULT_DB_ALIAS].settings_dict)
        test_connection.settings_dict['NAME'] = None
        test_connection.settings_dict['TEST']['NAME'] = 'custom.sqlite.db'
        signature = test_connection.creation_class(test_connection).test_db_signature()
        self.assertEqual(signature, (None, 'custom.sqlite.db'))
