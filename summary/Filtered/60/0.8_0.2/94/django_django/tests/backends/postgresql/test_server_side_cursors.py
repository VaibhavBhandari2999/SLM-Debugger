import operator
import unittest
from collections import namedtuple
from contextlib import contextmanager

from django.db import connection, models
from django.test import TestCase

from ..models import Person


@unittest.skipUnless(connection.vendor == "postgresql", "PostgreSQL tests")
class ServerSideCursorsPostgres(TestCase):
    cursor_fields = (
        "name, statement, is_holdable, is_binary, is_scrollable, creation_time"
    )
    PostgresCursor = namedtuple("PostgresCursor", cursor_fields)

    @classmethod
    def setUpTestData(cls):
        Person.objects.create(first_name="a", last_name="a")
        Person.objects.create(first_name="b", last_name="b")

    def inspect_cursors(self):
        """
        Inspect and retrieve active cursors from the PostgreSQL database.
        
        This function fetches information about active cursors from the `pg_cursors` system catalog.
        
        Parameters:
        None
        
        Returns:
        list: A list of `PostgresCursor` objects, each representing an active cursor in the database.
        """

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT {fields} FROM pg_cursors;".format(fields=self.cursor_fields)
            )
            cursors = cursor.fetchall()
        return [self.PostgresCursor._make(cursor) for cursor in cursors]

    @contextmanager
    def override_db_setting(self, **kwargs):
        """
        Override database settings temporarily for the duration of the test.
        
        This function allows you to override database settings for the duration of a test. It ensures that the original settings are restored after the test completes.
        
        Parameters:
        **kwargs: A dictionary where keys are the names of the database settings to override and values are the new settings.
        
        Yield:
        None: This function does not return a value, but it yields control to the test code during the override period.
        
        Example Usage:
        with self.override_db
        """

        for setting in kwargs:
            original_value = connection.settings_dict.get(setting)
            if setting in connection.settings_dict:
                self.addCleanup(
                    operator.setitem, connection.settings_dict, setting, original_value
                )
            else:
                self.addCleanup(operator.delitem, connection.settings_dict, setting)

            connection.settings_dict[setting] = kwargs[setting]
            yield

    def assertUsesCursor(self, queryset, num_expected=1):
        next(queryset)  # Open a server-side cursor
        cursors = self.inspect_cursors()
        self.assertEqual(len(cursors), num_expected)
        for cursor in cursors:
            self.assertIn("_django_curs_", cursor.name)
            self.assertFalse(cursor.is_scrollable)
            self.assertFalse(cursor.is_holdable)
            self.assertFalse(cursor.is_binary)

    def asserNotUsesCursor(self, queryset):
        self.assertUsesCursor(queryset, num_expected=0)

    def test_server_side_cursor(self):
        self.assertUsesCursor(Person.objects.iterator())

    def test_values(self):
        self.assertUsesCursor(Person.objects.values("first_name").iterator())

    def test_values_list(self):
        self.assertUsesCursor(Person.objects.values_list("first_name").iterator())

    def test_values_list_flat(self):
        """
        Asserts that the provided query uses a cursor for iteration on a values_list query with the flat=True parameter. The function takes a Django QuerySet object as an argument and checks if it uses a cursor for iteration. The values_list method is used to retrieve the first_name field from the Person model as a flat list, and the flat=True parameter ensures that the results are returned as a flat list rather than a list of tuples. The iterator method is used to return an iterator that yields the results one
        """

        self.assertUsesCursor(
            Person.objects.values_list("first_name", flat=True).iterator()
        )

    def test_values_list_fields_not_equal_to_names(self):
        expr = models.Count("id")
        self.assertUsesCursor(
            Person.objects.annotate(id__count=expr)
            .values_list(expr, "id__count")
            .iterator()
        )

    def test_server_side_cursor_many_cursors(self):
        persons = Person.objects.iterator()
        persons2 = Person.objects.iterator()
        next(persons)  # Open a server-side cursor
        self.assertUsesCursor(persons2, num_expected=2)

    def test_closed_server_side_cursor(self):
        persons = Person.objects.iterator()
        next(persons)  # Open a server-side cursor
        del persons
        cursors = self.inspect_cursors()
        self.assertEqual(len(cursors), 0)

    def test_server_side_cursors_setting(self):
        """
        Tests the behavior of server-side cursors in database queries.
        
        This function tests the impact of the `DISABLE_SERVER_SIDE_CURSORS` setting on database query cursors. It checks whether server-side cursors are used when the setting is disabled and ensures they are not used when the setting is enabled.
        
        Key Parameters:
        - None
        
        Keywords:
        - `DISABLE_SERVER_SIDE_CURSORS`: A setting that controls whether server-side cursors should be used.
        
        Inputs:
        - The function uses the `override_db
        """

        with self.override_db_setting(DISABLE_SERVER_SIDE_CURSORS=False):
            persons = Person.objects.iterator()
            self.assertUsesCursor(persons)
            del persons  # Close server-side cursor

        with self.override_db_setting(DISABLE_SERVER_SIDE_CURSORS=True):
            self.asserNotUsesCursor(Person.objects.iterator())
