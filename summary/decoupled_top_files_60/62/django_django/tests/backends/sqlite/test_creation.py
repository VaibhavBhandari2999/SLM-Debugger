import copy
import unittest

from django.db import DEFAULT_DB_ALIAS, connection, connections
from django.test import SimpleTestCase


@unittest.skipUnless(connection.vendor == 'sqlite', 'SQLite tests')
class TestDbSignatureTests(SimpleTestCase):
    def test_custom_test_name(self):
        """
        Tests the database connection with a custom test name.
        
        This function creates a copy of the default database connection and modifies its settings to use a custom test database name. It then generates a test database signature based on these settings and asserts that the signature matches the expected format.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - `test_connection`: A copy of the default database connection with modified settings for testing.
        
        Keywords:
        - `connections`: A dictionary containing database connections.
        -
        """

        test_connection = copy.copy(connections[DEFAULT_DB_ALIAS])
        test_connection.settings_dict = copy.deepcopy(connections[DEFAULT_DB_ALIAS].settings_dict)
        test_connection.settings_dict['NAME'] = None
        test_connection.settings_dict['TEST']['NAME'] = 'custom.sqlite.db'
        signature = test_connection.creation_class(test_connection).test_db_signature()
        self.assertEqual(signature, (None, 'custom.sqlite.db'))
