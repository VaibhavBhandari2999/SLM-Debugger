import copy
import unittest

from django.db import DEFAULT_DB_ALIAS, connection, connections
from django.test import SimpleTestCase


@unittest.skipUnless(connection.vendor == 'sqlite', 'SQLite tests')
class TestDbSignatureTests(SimpleTestCase):
    def test_custom_test_name(self):
        """
        Tests a custom database connection setup.
        
        This function sets up a custom database connection for testing purposes. It creates a copy of the default database connection and modifies its settings to use a custom SQLite database file named 'custom.sqlite.db'. The function then generates a test database signature based on the modified connection settings and asserts that the signature is as expected.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - `connections[DEFAULT_DB_ALIAS]`: The default database connection settings.
        
        Keywords:
        """

        test_connection = copy.copy(connections[DEFAULT_DB_ALIAS])
        test_connection.settings_dict = copy.deepcopy(connections[DEFAULT_DB_ALIAS].settings_dict)
        test_connection.settings_dict['NAME'] = None
        test_connection.settings_dict['TEST']['NAME'] = 'custom.sqlite.db'
        signature = test_connection.creation_class(test_connection).test_db_signature()
        self.assertEqual(signature, (None, 'custom.sqlite.db'))
