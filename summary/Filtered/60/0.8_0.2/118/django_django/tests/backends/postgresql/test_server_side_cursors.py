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
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT {fields} FROM pg_cursors;".format(fields=self.cursor_fields)
            )
            cursors = cursor.fetchall()
        return [self.PostgresCursor._make(cursor) for cursor in cursors]

    @contextmanager
    def override_db_setting(self, **kwargs):
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
        Asserts that the provided query uses a cursor. The query in question is `Person.objects.values_list("first_name", flat=True).iterator()`. This method checks if the query is executed with a cursor, which is necessary for handling large result sets efficiently. The parameters are:
        - `query`: The query to be checked, in this case, `Person.objects.values_list("first_name", flat=True).iterator()`.
        
        The function does not return any value; it raises an assertion error if the
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
        """
        Tests the behavior of a closed server-side cursor.
        
        This function checks whether a server-side cursor is properly closed after being iterated over and then deleted. It opens a server-side cursor by iterating over the `Person` objects, consumes the first item, and then deletes the cursor. The function then inspects the cursors and asserts that the length of the list of cursors is zero, indicating that the cursor has been closed.
        
        Parameters:
        None
        
        Returns:
        None
        
        Keywords:
        None
        """

        persons = Person.objects.iterator()
        next(persons)  # Open a server-side cursor
        del persons
        cursors = self.inspect_cursors()
        self.assertEqual(len(cursors), 0)

    def test_server_side_cursors_setting(self):
        with self.override_db_setting(DISABLE_SERVER_SIDE_CURSORS=False):
            persons = Person.objects.iterator()
            self.assertUsesCursor(persons)
            del persons  # Close server-side cursor

        with self.override_db_setting(DISABLE_SERVER_SIDE_CURSORS=True):
            self.asserNotUsesCursor(Person.objects.iterator())
