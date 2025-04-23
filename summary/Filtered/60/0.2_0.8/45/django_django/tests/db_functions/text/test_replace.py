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
        Tests the functionality of the Replace function in Django's ORM.
        
        This function tests the Replace function by annotating a queryset of Author objects with a new field 'without_middlename' that replaces the substring 'R. R. ' in the 'name' field with an empty string. The expected output is a queryset with two elements, where the 'name' field is transformed as specified.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - The resulting queryset should contain two elements, where
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
        # The default replacement is an empty string.
        qs = Author.objects.annotate(same_name=Replace(F('name'), Value('R. R. ')))
        self.assertQuerysetEqual(qs, [
            ('George R. R. Martin', 'George Martin'),
            ('J. R. R. Tolkien', 'J. Tolkien'),
        ], transform=lambda x: (x.name, x.same_name), ordered=False)
