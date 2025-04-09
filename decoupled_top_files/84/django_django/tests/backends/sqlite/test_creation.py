"""
```markdown
This Python script contains unit tests for database connection settings in Django applications, specifically focusing on SQLite databases. It includes two test methods:

1. `test_custom_test_name`: Verifies the custom test database name functionality by creating a modified copy of the default database connection and checking the test database signature.
2. `test_get_test_db_clone_settings_name`: Tests the `get_test_db_clone_settings` method of the database connection's creation class by cloning the settings for different test database names.

The tests utilize Django's `SimpleTestCase` and `unittest` framework to ensure that the database connection settings are correctly configured and cloned as expected.
```

### Docstring:
```python
"""
import copy
import unittest

from django.db import DEFAULT_DB_ALIAS, connection, connections
from django.test import SimpleTestCase


@unittest.skipUnless(connection.vendor == 'sqlite', 'SQLite tests')
class TestDbSignatureTests(SimpleTestCase):
    def test_custom_test_name(self):
        """
        Tests the custom test name functionality by creating a copy of the default database connection, modifying its settings to use a custom test database name, and verifying the test database signature.
        
        Args:
        self: The instance of the class containing this method.
        
        Returns:
        None
        
        Functions Used:
        - `copy.copy()`: Creates a shallow copy of the default database connection.
        - `copy.deepcopy()`: Creates a deep copy of the default database connection's settings dictionary.
        - `connections
        """

        test_connection = copy.copy(connections[DEFAULT_DB_ALIAS])
        test_connection.settings_dict = copy.deepcopy(connections[DEFAULT_DB_ALIAS].settings_dict)
        test_connection.settings_dict['NAME'] = None
        test_connection.settings_dict['TEST']['NAME'] = 'custom.sqlite.db'
        signature = test_connection.creation_class(test_connection).test_db_signature()
        self.assertEqual(signature, (None, 'custom.sqlite.db'))

    def test_get_test_db_clone_settings_name(self):
        """
        This function tests the `get_test_db_clone_settings` method of the `creation_class` for a database connection. It creates a copy of the default database connection and sets its settings dictionary to a deep copy of the default settings. The function then iterates over a list of test database names and their expected cloned names. For each test case, it updates the connection's settings dictionary with the current test database name and calls the `get_test_db_clone_settings` method with an index of '1'.
        """

        test_connection = copy.copy(connections[DEFAULT_DB_ALIAS])
        test_connection.settings_dict = copy.deepcopy(
            connections[DEFAULT_DB_ALIAS].settings_dict,
        )
        tests = [
            ('test.sqlite3', 'test_1.sqlite3'),
            ('test', 'test_1'),
        ]
        for test_db_name, expected_clone_name in tests:
            with self.subTest(test_db_name=test_db_name):
                test_connection.settings_dict['NAME'] = test_db_name
                test_connection.settings_dict['TEST']['NAME'] = test_db_name
                creation_class = test_connection.creation_class(test_connection)
                clone_settings_dict = creation_class.get_test_db_clone_settings('1')
                self.assertEqual(clone_settings_dict['NAME'], expected_clone_name)
