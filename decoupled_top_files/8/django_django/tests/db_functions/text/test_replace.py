"""
This Python file contains unit tests for the `Replace` function in Django ORM. It includes several test cases to validate different scenarios involving string replacements within the `name` field of `Author` model instances. The tests cover various aspects such as case sensitivity, concatenation, and updating database records. Each test method provides detailed documentation explaining its purpose, arguments, and expected outcomes. The file uses Django's testing framework (`TestCase`) and ORM features like `annotate`, `Replace`, `F`, and `Value` to perform these validations. ```python
"""
from django.db.models import F, Value
from django.db.models.functions import Concat, Replace
from django.test import TestCase

from ..models import Author


class ReplaceTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        Author.objects.create(name='George R. R. Martin')
        Author.objects.create(name='J. R. R. Tolkien')

    def test_replace_with_empty_string(self):
        """
        Replaces occurrences of 'R. R. ' with an empty string in the 'name' field of Author objects.
        
        Args:
        None
        
        Returns:
        A queryset containing Author objects with their original names and modified names without 'R. R.'.
        
        Example:
        Given the following authors:
        - George R. R. Martin
        - J. R. R. Tolkien
        
        The function will return:
        - ('George R. R. Martin', 'George Martin
        """

        qs = Author.objects.annotate(
            without_middlename=Replace(F('name'), Value('R. R. '), Value('')),
        )
        self.assertQuerysetEqual(qs, [
            ('George R. R. Martin', 'George Martin'),
            ('J. R. R. Tolkien', 'J. Tolkien'),
        ], transform=lambda x: (x.name, x.without_middlename), ordered=False)

    def test_case_sensitive(self):
        """
        Tests case sensitivity by replacing 'r. r.' with an empty string in the 'name' field of Author objects and comparing the results.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `annotate`: Adds a new field to each element of the queryset based on the given expression.
        - `Replace`: Replaces occurrences of a specified value in a field with another value.
        - `F`: Represents an expression referring to a field in the query.
        """

        qs = Author.objects.annotate(same_name=Replace(F('name'), Value('r. r.'), Value('')))
        self.assertQuerysetEqual(qs, [
            ('George R. R. Martin', 'George R. R. Martin'),
            ('J. R. R. Tolkien', 'J. R. R. Tolkien'),
        ], transform=lambda x: (x.name, x.same_name), ordered=False)

    def test_replace_expression(self):
        """
        Tests the functionality of the `annotate` method with the `Replace` and `Concat` functions. The `annotate` method is used to add a new field `same_name` to each object in the queryset by replacing the substring 'Author: ' at the beginning of the name with an empty string. The resulting queryset is then compared to a list of expected tuples containing the original names and their corresponding modified names.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError
        """

        qs = Author.objects.annotate(same_name=Replace(
            Concat(Value('Author: '), F('name')), Value('Author: '), Value('')),
        )
        self.assertQuerysetEqual(qs, [
            ('George R. R. Martin', 'George R. R. Martin'),
            ('J. R. R. Tolkien', 'J. R. R. Tolkien'),
        ], transform=lambda x: (x.name, x.same_name), ordered=False)

    def test_update(self):
        """
        Updates the 'name' field of all Author objects by removing 'R. R. ' from the beginning of each name. The updated names are then compared against a predefined list of expected names using assertQuerysetEqual.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - Author.objects.update(): Updates the 'name' field of Author objects.
        - Replace(): Replaces a specified substring with another substring.
        - Value(): Represents a value expression in Django queries
        """

        Author.objects.update(
            name=Replace(F('name'), Value('R. R. '), Value('')),
        )
        self.assertQuerysetEqual(Author.objects.all(), [
            ('George Martin'),
            ('J. Tolkien'),
        ], transform=lambda x: x.name, ordered=False)

    def test_replace_with_default_arg(self):
        """
        Tests the `Replace` function with a default argument of an empty string, replacing occurrences of 'R. R. ' in the 'name' field of Author objects with an empty string. The resulting queryset contains tuples of the original name and the modified name.
        """

        # The default replacement is an empty string.
        qs = Author.objects.annotate(same_name=Replace(F('name'), Value('R. R. ')))
        self.assertQuerysetEqual(qs, [
            ('George R. R. Martin', 'George Martin'),
            ('J. R. R. Tolkien', 'J. Tolkien'),
        ], transform=lambda x: (x.name, x.same_name), ordered=False)
