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
        Tests the functionality of the `Replace` function in Django's ORM.
        
        This function creates a queryset of authors and annotates each author with a new field `without_middlename`.
        The `without_middlename` field is created by replacing the substring 'R. R. ' in the `name` field with an empty string.
        The expected output is a list of tuples, each containing the original name and the modified name without the middle part.
        
        Parameters:
        - None
        
        Returns:
        - None
        """

        qs = Author.objects.annotate(
            without_middlename=Replace(F('name'), Value('R. R. '), Value('')),
        )
        self.assertQuerysetEqual(qs, [
            ('George R. R. Martin', 'George Martin'),
            ('J. R. R. Tolkien', 'J. Tolkien'),
        ], transform=lambda x: (x.name, x.without_middlename), ordered=False)

    def test_case_sensitive(self):
        qs = Author.objects.annotate(same_name=Replace(F('name'), Value('r. r.'), Value('')))
        self.assertQuerysetEqual(qs, [
            ('George R. R. Martin', 'George R. R. Martin'),
            ('J. R. R. Tolkien', 'J. R. R. Tolkien'),
        ], transform=lambda x: (x.name, x.same_name), ordered=False)

    def test_replace_expression(self):
        qs = Author.objects.annotate(same_name=Replace(
            Concat(Value('Author: '), F('name')), Value('Author: '), Value('')),
        )
        self.assertQuerysetEqual(qs, [
            ('George R. R. Martin', 'George R. R. Martin'),
            ('J. R. R. Tolkien', 'J. R. R. Tolkien'),
        ], transform=lambda x: (x.name, x.same_name), ordered=False)

    def test_update(self):
        Author.objects.update(
            name=Replace(F('name'), Value('R. R. '), Value('')),
        )
        self.assertQuerysetEqual(Author.objects.all(), [
            ('George Martin'),
            ('J. Tolkien'),
        ], transform=lambda x: x.name, ordered=False)

    def test_replace_with_default_arg(self):
        """
        Tests the replace_with_default_arg method which annotates a queryset with a modified name by replacing 'R. R. ' with an empty string. The method takes no parameters and returns a queryset. The expected output is a queryset with two elements, each containing a tuple of the original name and the modified name.
        
        Parameters:
        - None
        
        Returns:
        - A queryset with annotated 'same_name' field.
        
        Example Usage:
        ```python
        qs = Author.objects.annotate(same_name=Replace(F('name'),
        """

        # The default replacement is an empty string.
        qs = Author.objects.annotate(same_name=Replace(F('name'), Value('R. R. ')))
        self.assertQuerysetEqual(qs, [
            ('George R. R. Martin', 'George Martin'),
            ('J. R. R. Tolkien', 'J. Tolkien'),
        ], transform=lambda x: (x.name, x.same_name), ordered=False)
