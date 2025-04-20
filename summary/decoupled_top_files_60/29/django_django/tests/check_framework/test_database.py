import unittest
from unittest import mock

from django.core.checks import Tags, run_checks
from django.core.checks.registry import CheckRegistry
from django.db import connection
from django.test import TestCase


class DatabaseCheckTests(TestCase):
    databases = {'default', 'other'}

    @property
    def func(self):
        from django.core.checks.database import check_database_backends
        return check_database_backends

    def test_database_checks_not_run_by_default(self):
        """
        `database` checks are only run when their tag is specified.
        """
        def f1(**kwargs):
            return [5]

        registry = CheckRegistry()
        registry.register(Tags.database)(f1)
        errors = registry.run_checks()
        self.assertEqual(errors, [])

        errors2 = registry.run_checks(tags=[Tags.database])
        self.assertEqual(errors2, [5])

    def test_database_checks_called(self):
        """
        Tests if the database checks are called during the validation process.
        
        This function patches the `check` method from `BaseDatabaseValidation` in `django.db.backends.base.validation` to ensure it is called when running checks with the `database` tag.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - Uses `mock.patch` to temporarily replace the `check` method.
        - Calls `run_checks` with the `database` tag.
        - Asserts that the `check` method was
        """

        with mock.patch('django.db.backends.base.validation.BaseDatabaseValidation.check') as mocked_check:
            run_checks(tags=[Tags.database])
            self.assertTrue(mocked_check.called)

    @unittest.skipUnless(connection.vendor == 'mysql', 'Test only for MySQL')
    def test_mysql_strict_mode(self):
        """
        Tests the MySQL strict mode setting.
        
        This function checks if the MySQL strict mode is set correctly. It uses a mock patch to simulate the response from the database for the SQL modes. The function iterates over a list of expected good SQL modes and a list of expected bad SQL modes. For each mode, it patches the `CursorWrapper.fetchone` method to return the respective mode and then calls the `func` with the mode as `None`. If the mode is in the good list, it expects
        """

        good_sql_modes = [
            'STRICT_TRANS_TABLES,STRICT_ALL_TABLES',
            'STRICT_TRANS_TABLES',
            'STRICT_ALL_TABLES',
        ]
        for response in good_sql_modes:
            with mock.patch(
                'django.db.backends.utils.CursorWrapper.fetchone', create=True,
                return_value=(response,)
            ):
                self.assertEqual(self.func(None), [])

        bad_sql_modes = ['', 'WHATEVER']
        for response in bad_sql_modes:
            with mock.patch(
                'django.db.backends.utils.CursorWrapper.fetchone', create=True,
                return_value=(response,)
            ):
                # One warning for each database alias
                result = self.func(None)
                self.assertEqual(len(result), 2)
                self.assertEqual([r.id for r in result], ['mysql.W002', 'mysql.W002'])
