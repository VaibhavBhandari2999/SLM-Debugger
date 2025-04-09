import os
import re
import tempfile
import threading
import unittest
from pathlib import Path
from sqlite3 import dbapi2
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.db import ConnectionHandler, connection, transaction
from django.db.models import Avg, StdDev, Sum, Variance
from django.db.models.aggregates import Aggregate
from django.db.models.fields import CharField
from django.db.utils import NotSupportedError
from django.test import (
    TestCase, TransactionTestCase, override_settings, skipIfDBFeature,
)
from django.test.utils import isolate_apps

from ..models import Author, Item, Object, Square

try:
    from django.db.backends.sqlite3.base import check_sqlite_version
except ImproperlyConfigured:
    # Ignore "SQLite is too old" when running tests on another database.
    pass


@unittest.skipUnless(connection.vendor == 'sqlite', 'SQLite tests')
class Tests(TestCase):
    longMessage = True

    def test_check_sqlite_version(self):
        """
        Tests the `check_sqlite_version` function.
        
        This test checks that the `check_sqlite_version` function raises an `ImproperlyConfigured` exception with the message 'SQLite 3.8.3 or later is required (found 3.8.2)' when SQLite version 3.8.2 is detected. It uses mocking to set the `sqlite_version_info` and `sqlite_version` attributes of the `dbapi2` module to simulate the SQLite version being
        """

        msg = 'SQLite 3.8.3 or later is required (found 3.8.2).'
        with mock.patch.object(dbapi2, 'sqlite_version_info', (3, 8, 2)), \
                mock.patch.object(dbapi2, 'sqlite_version', '3.8.2'), \
                self.assertRaisesMessage(ImproperlyConfigured, msg):
            check_sqlite_version()

    def test_aggregation(self):
        """
        Raise NotImplementedError when aggregating on date/time fields (#19360).
        """
        for aggregate in (Sum, Avg, Variance, StdDev):
            with self.assertRaises(NotSupportedError):
                Item.objects.all().aggregate(aggregate('time'))
            with self.assertRaises(NotSupportedError):
                Item.objects.all().aggregate(aggregate('date'))
            with self.assertRaises(NotSupportedError):
                Item.objects.all().aggregate(aggregate('last_modified'))
            with self.assertRaises(NotSupportedError):
                Item.objects.all().aggregate(
                    **{'complex': aggregate('last_modified') + aggregate('last_modified')}
                )

    def test_distinct_aggregation(self):
        """
        Raises a NotSupportedError if attempting to use DISTINCT with an aggregate function that accepts multiple arguments in SQLite.
        
        Args:
        aggregate (DistinctAggregate): An instance of the DistinctAggregate class, which is an aggregate function allowing DISTINCT.
        
        Raises:
        NotSupportedError: If the aggregate function attempts to use DISTINCT with multiple arguments, as this is not supported by SQLite.
        
        Usage:
        This function checks whether the provided aggregate function can be used with DISTINCT in SQLite. It ensures that only single
        """

        class DistinctAggregate(Aggregate):
            allow_distinct = True
        aggregate = DistinctAggregate('first', 'second', distinct=True)
        msg = (
            "SQLite doesn't support DISTINCT on aggregate functions accepting "
            "multiple arguments."
        )
        with self.assertRaisesMessage(NotSupportedError, msg):
            connection.ops.check_expression_support(aggregate)

    def test_memory_db_test_name(self):
        """A named in-memory db should be allowed where supported."""
        from django.db.backends.sqlite3.base import DatabaseWrapper
        settings_dict = {
            'TEST': {
                'NAME': 'file:memorydb_test?mode=memory&cache=shared',
            }
        }
        creation = DatabaseWrapper(settings_dict).creation
        self.assertEqual(creation._get_test_db_name(), creation.connection.settings_dict['TEST']['NAME'])

    def test_regexp_function(self):
        """
        Tests a string against a regular expression pattern.
        
        Args:
        string (str or None): The string to be tested.
        pattern (str or None): The regular expression pattern to match the string against.
        expected (bool or None): The expected result of the regular expression match.
        
        Returns:
        bool: The result of the regular expression match.
        
        Notes:
        - The function uses a database cursor to execute a SQL query that performs the regular expression match.
        - The result is
        """

        tests = (
            ('test', r'[0-9]+', False),
            ('test', r'[a-z]+', True),
            ('test', None, None),
            (None, r'[a-z]+', None),
            (None, None, None),
        )
        for string, pattern, expected in tests:
            with self.subTest((string, pattern)):
                with connection.cursor() as cursor:
                    cursor.execute('SELECT %s REGEXP %s', [string, pattern])
                    value = cursor.fetchone()[0]
                value = bool(value) if value in {0, 1} else value
                self.assertIs(value, expected)

    def test_pathlib_name(self):
        """
        Test the creation and deletion of a SQLite database using pathlib.Path.
        
        This function creates a temporary directory, sets up a Django database
        configuration using `pathlib.Path` to specify the database name, ensures
        the connection is established, closes the connection, and verifies that
        the database file has been created in the specified directory.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `tempfile.TemporaryDirectory`: Creates a temporary directory.
        """

        with tempfile.TemporaryDirectory() as tmp:
            settings_dict = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': Path(tmp) / 'test.db',
                },
            }
            connections = ConnectionHandler(settings_dict)
            connections['default'].ensure_connection()
            connections['default'].close()
            self.assertTrue(os.path.isfile(os.path.join(tmp, 'test.db')))


@unittest.skipUnless(connection.vendor == 'sqlite', 'SQLite tests')
@isolate_apps('backends')
class SchemaTests(TransactionTestCase):

    available_apps = ['backends']

    def test_autoincrement(self):
        """
        auto_increment fields are created with the AUTOINCREMENT keyword
        in order to be monotonically increasing (#10164).
        """
        with connection.schema_editor(collect_sql=True) as editor:
            editor.create_model(Square)
            statements = editor.collected_sql
        match = re.search('"id" ([^,]+),', statements[0])
        self.assertIsNotNone(match)
        self.assertEqual(
            'integer NOT NULL PRIMARY KEY AUTOINCREMENT',
            match.group(1),
            'Wrong SQL used to create an auto-increment column on SQLite'
        )

    def test_disable_constraint_checking_failure_disallowed(self):
        """
        SQLite schema editor is not usable within an outer transaction if
        foreign key constraint checks are not disabled beforehand.
        """
        msg = (
            'SQLite schema editor cannot be used while foreign key '
            'constraint checks are enabled. Make sure to disable them '
            'before entering a transaction.atomic() context because '
            'SQLite does not support disabling them in the middle of '
            'a multi-statement transaction.'
        )
        with self.assertRaisesMessage(NotSupportedError, msg):
            with transaction.atomic(), connection.schema_editor(atomic=True):
                pass

    def test_constraint_checks_disabled_atomic_allowed(self):
        """
        SQLite schema editor is usable within an outer transaction as long as
        foreign key constraints checks are disabled beforehand.
        """
        def constraint_checks_enabled():
            with connection.cursor() as cursor:
                return bool(cursor.execute('PRAGMA foreign_keys').fetchone()[0])
        with connection.constraint_checks_disabled(), transaction.atomic():
            with connection.schema_editor(atomic=True):
                self.assertFalse(constraint_checks_enabled())
            self.assertFalse(constraint_checks_enabled())
        self.assertTrue(constraint_checks_enabled())

    @skipIfDBFeature('supports_atomic_references_rename')
    def test_field_rename_inside_atomic_block(self):
        """
        NotImplementedError is raised when a model field rename is attempted
        inside an atomic block.
        """
        new_field = CharField(max_length=255, unique=True)
        new_field.set_attributes_from_name('renamed')
        msg = (
            "Renaming the 'backends_author'.'name' column while in a "
            "transaction is not supported on SQLite < 3.26 because it would "
            "break referential integrity. Try adding `atomic = False` to the "
            "Migration class."
        )
        with self.assertRaisesMessage(NotSupportedError, msg):
            with connection.schema_editor(atomic=True) as editor:
                editor.alter_field(Author, Author._meta.get_field('name'), new_field)

    @skipIfDBFeature('supports_atomic_references_rename')
    def test_table_rename_inside_atomic_block(self):
        """
        NotImplementedError is raised when a table rename is attempted inside
        an atomic block.
        """
        msg = (
            "Renaming the 'backends_author' table while in a transaction is "
            "not supported on SQLite < 3.26 because it would break referential "
            "integrity. Try adding `atomic = False` to the Migration class."
        )
        with self.assertRaisesMessage(NotSupportedError, msg):
            with connection.schema_editor(atomic=True) as editor:
                editor.alter_db_table(Author, "backends_author", "renamed_table")


@unittest.skipUnless(connection.vendor == 'sqlite', 'Test only for SQLite')
@override_settings(DEBUG=True)
class LastExecutedQueryTest(TestCase):

    def test_no_interpolation(self):
        """
        Tests that SQL queries with strftime formatting do not raise exceptions when executed directly, ensuring the query's SQL remains unchanged after execution. The function uses the `strftime` function to format the current year and executes the query using the cursor object from the database connection. The expected outcome is that the query's SQL remains the same as the input query.
        """

        # This shouldn't raise an exception (#17158)
        query = "SELECT strftime('%Y', 'now');"
        connection.cursor().execute(query)
        self.assertEqual(connection.queries[-1]['sql'], query)

    def test_parameter_quoting(self):
        """
        Tests that parameters are correctly quoted when executing SQL queries. This function checks if the `last_executed_queries` method of the connection object is functioning properly by verifying that parameters are appropriately quoted. The function takes a SQL query with a placeholder for parameters and a list of parameters to be inserted into the query. It then executes the query using the cursor object from the connection and compares the resulting SQL statement with the expected output.
        
        Args:
        self: The instance of the class containing this method.
        """

        # The implementation of last_executed_queries isn't optimal. It's
        # worth testing that parameters are quoted (#14091).
        query = "SELECT %s"
        params = ["\"'\\"]
        connection.cursor().execute(query, params)
        # Note that the single quote is repeated
        substituted = "SELECT '\"''\\'"
        self.assertEqual(connection.queries[-1]['sql'], substituted)

    def test_large_number_of_parameters(self):
        """
        Tests the behavior of `last_executed_query` method when dealing with a large number of parameters. This method is called with a SQL query containing 2001 placeholders, which simulates a scenario where the number of parameters exceeds the default SQLite limits (`SQLITE_MAX_VARIABLE_NUMBER` and `SQLITE_MAX_COLUMN`). The function ensures that no exceptions are raised under such conditions.
        
        Args:
        self: The instance of the class containing this method.
        
        Returns:
        None
        
        Notes
        """

        # If SQLITE_MAX_VARIABLE_NUMBER (default = 999) has been changed to be
        # greater than SQLITE_MAX_COLUMN (default = 2000), last_executed_query
        # can hit the SQLITE_MAX_COLUMN limit (#26063).
        with connection.cursor() as cursor:
            sql = "SELECT MAX(%s)" % ", ".join(["%s"] * 2001)
            params = list(range(2001))
            # This should not raise an exception.
            cursor.db.ops.last_executed_query(cursor.cursor, sql, params)


@unittest.skipUnless(connection.vendor == 'sqlite', 'SQLite tests')
class EscapingChecks(TestCase):
    """
    All tests in this test case are also run with settings.DEBUG=True in
    EscapingChecksDebug test case, to also test CursorDebugWrapper.
    """
    def test_parameter_escaping(self):
        """
        Tests parameter escaping using the strftime and date functions in SQLite3, ensuring the response is a non-zero integer.
        """

        # '%s' escaping support for sqlite3 (#13648).
        with connection.cursor() as cursor:
            cursor.execute("select strftime('%s', date('now'))")
            response = cursor.fetchall()[0][0]
        # response should be an non-zero integer
        self.assertTrue(int(response))


@unittest.skipUnless(connection.vendor == 'sqlite', 'SQLite tests')
@override_settings(DEBUG=True)
class EscapingChecksDebug(EscapingChecks):
    pass


@unittest.skipUnless(connection.vendor == 'sqlite', 'SQLite tests')
class ThreadSharing(TransactionTestCase):
    available_apps = ['backends']

    def test_database_sharing_in_threads(self):
        """
        Tests database sharing in threads.
        
        This function creates an object using `Object.objects.create()` and then
        creates a new thread to run the same operation. After joining the thread,
        it asserts that there are two objects in the database, indicating proper
        database sharing between threads.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `Object.objects.create()`: Creates a new object in the database.
        - `threading.Thread(target=create_object)
        """

        def create_object():
            Object.objects.create()
        create_object()
        thread = threading.Thread(target=create_object)
        thread.start()
        thread.join()
        self.assertEqual(Object.objects.count(), 2)
