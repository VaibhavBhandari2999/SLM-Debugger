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
        """
        Assert that a queryset uses a specified number of server-side cursors.
        
        Args:
        queryset (QuerySet): The queryset to test.
        num_expected (int, optional): The expected number of cursors. Defaults to 1.
        
        This function opens a server-side cursor by iterating over the queryset, inspects the cursors used, and checks that the correct number of cursors are created with the expected properties. Each cursor should have a name containing "_django_curs_", and should not be scroll
        """

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
        """
        Tests the behavior of server-side cursors with multiple cursors.
        
        This function creates two iterators for the Person model objects using the `iterator` method. It then opens a server-side cursor by calling `next` on the first iterator. The function asserts that the second iterator can still fetch the expected number of objects.
        
        Parameters:
        None
        
        Keywords:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the second iterator does not fetch the expected number of objects.
        """

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
        Tests the behavior of server-side cursors based on the `DISABLE_SERVER_SIDE_CURSORS` setting.
        
        This function checks whether server-side cursors are enabled or disabled by setting the `DISABLE_SERVER_SIDE_CURSORS` setting. It then queries the `Person` model using an iterator and verifies whether server-side cursors are used or not.
        
        Parameters:
        - None
        
        Keywords:
        - None
        
        Returns:
        - None
        
        Key Steps:
        1. Temporarily sets `DISABLE_SERVER_SIDE_CURSORS`
        """

        with self.override_db_setting(DISABLE_SERVER_SIDE_CURSORS=False):
            persons = Person.objects.iterator()
            self.assertUsesCursor(persons)
            del persons  # Close server-side cursor

        with self.override_db_setting(DISABLE_SERVER_SIDE_CURSORS=True):
            self.asserNotUsesCursor(Person.objects.iterator())
