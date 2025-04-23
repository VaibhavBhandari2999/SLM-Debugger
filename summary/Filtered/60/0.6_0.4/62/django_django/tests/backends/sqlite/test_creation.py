import copy
import unittest

from django.db import DEFAULT_DB_ALIAS, connection, connections
from django.test import SimpleTestCase


@unittest.skipUnless(connection.vendor == 'sqlite', 'SQLite tests')
class TestDbSignatureTests(SimpleTestCase):
    def test_custom_test_name(self):
        """
        Tests a custom test database name.
        
        This function creates a copy of the default database connection and modifies its settings to use a custom test database name. It then generates a test database signature based on the modified connection settings.
        
        Parameters:
        None
        
        Returns:
        tuple: A tuple containing the database name and the custom test database name.
        """

        test_connection = copy.copy(connections[DEFAULT_DB_ALIAS])
        test_connection.settings_dict = copy.deepcopy(connections[DEFAULT_DB_ALIAS].settings_dict)
        test_connection.settings_dict['NAME'] = None
        test_connection.settings_dict['TEST']['NAME'] = 'custom.sqlite.db'
        signature = test_connection.creation_class(test_connection).test_db_signature()
        self.assertEqual(signature, (None, 'custom.sqlite.db'))
