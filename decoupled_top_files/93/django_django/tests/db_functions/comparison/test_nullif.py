"""
The provided Python file contains unit tests for the Django ORM's `NullIf` function. The file defines a test class `NullIfTests` that inherits from `django.test.TestCase`. It includes several methods to test different aspects of the `NullIf` function:

1. **test_basic**: Tests the basic functionality of `annotate` combined with `NullIf` for handling null values. It queries the `Author` model, annotates each author's alias with `NullIf` against their name, and verifies the results.
2. **test_null_argument**: Tests the behavior of `NullIf` on `None` values in the `name` field. It annotates each author with the result of applying `NullIf` to their name
"""
from unittest import skipUnless

from django.db import connection
from django.db.models import Value
from django.db.models.functions import NullIf
from django.test import TestCase

from ..models import Author


class NullIfTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Author.objects.create(name="John Smith", alias="smithj")
        Author.objects.create(name="Rhonda", alias="Rhonda")

    def test_basic(self):
        """
        Tests the basic functionality of the `annotate` method combined with `NullIf` for handling null values. The function queries the `Author` model, annotates each author's alias with `NullIf` against their name, and then retrieves the annotated values. The expected output is a list of tuples containing the result of the `NullIf` operation, which may include an empty string or `None` based on the database's feature of interpreting empty strings as nulls.
        
        Args:
        None
        """

        authors = Author.objects.annotate(nullif=NullIf("alias", "name")).values_list(
            "nullif"
        )
        self.assertSequenceEqual(
            authors,
            [
                ("smithj",),
                (
                    ""
                    if connection.features.interprets_empty_strings_as_nulls
                    else None,
                ),
            ],
        )

    def test_null_argument(self):
        """
        Tests the behavior of the NullIf function on author names.
        
        This test checks how the NullIf function processes None values in the 'name' field of the Author model. It annotates each author with a 'nullif' value, which is the result of applying the NullIf function to their name and a None value. The expected output is a list of tuples containing the processed names, where any name that would have been None after applying NullIf is replaced by the original name.
        
        Args
        """

        authors = Author.objects.annotate(
            nullif=NullIf("name", Value(None))
        ).values_list("nullif")
        self.assertSequenceEqual(authors, [("John Smith",), ("Rhonda",)])

    def test_too_few_args(self):
        """
        Test that the 'NullIf' function raises a TypeError when fewer than two arguments are provided.
        
        Args:
        None
        
        Raises:
        TypeError: If 'NullIf' is called with fewer than two arguments.
        
        Example:
        >>> NullIf("name")
        Traceback (most recent call last):
        ...
        TypeError: 'NullIf' takes exactly 2 arguments (1 given)
        """

        msg = "'NullIf' takes exactly 2 arguments (1 given)"
        with self.assertRaisesMessage(TypeError, msg):
            NullIf("name")

    @skipUnless(connection.vendor == "oracle", "Oracle specific test for NULL-literal")
    def test_null_literal(self):
        """
        Test that Oracle raises a ValueError when attempting to use `Value(None)` in an expression.
        
        This function asserts that using `Value(None)` in an `annotate` call with `NullIf` results in a `ValueError` being raised. The error message should match the expected message: "Oracle does not allow Value(None) for expression1."
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the error message does not match the expected message.
        """

        msg = "Oracle does not allow Value(None) for expression1."
        with self.assertRaisesMessage(ValueError, msg):
            list(
                Author.objects.annotate(nullif=NullIf(Value(None), "name")).values_list(
                    "nullif"
                )
            )
