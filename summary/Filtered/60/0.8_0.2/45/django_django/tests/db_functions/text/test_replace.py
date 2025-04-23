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
        Tests the replace_with_empty_string function for the Author model.
        
        This function tests the replacement of a specific substring in the 'name' field of the Author model using the Replace function. The function replaces the substring 'R. R. ' with an empty string in the 'name' field.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        The function asserts that the queryset returned by the annotate method is equal to a list of tuples, where each tuple contains the original name and the modified
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
        Tests the case sensitivity of the name field in the Author model.
        
        This function checks if the name field in the Author model is case-sensitive by replacing the substring 'r. r.' with an empty string and comparing the results.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        The function asserts that the queryset matches the expected results, where the name 'r. r.' is replaced with an empty string.
        
        Expected Queryset:
        - ('George R. R. Martin', 'George
        """

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
        Tests the `Replace` function with a default replacement argument.
        
        This function tests the `Replace` function from Django's F expressions, which is used to replace a substring in a field value. The default replacement value is an empty string.
        
        Parameters:
        None
        
        Returns:
        None
        
        Example usage:
        The default replacement is an empty string.
        qs = Author.objects.annotate(same_name=Replace(F('name'), Value('R. R. ')))
        self.assertQuerysetEqual(qs
        """

        # The default replacement is an empty string.
        qs = Author.objects.annotate(same_name=Replace(F('name'), Value('R. R. ')))
        self.assertQuerysetEqual(qs, [
            ('George R. R. Martin', 'George Martin'),
            ('J. R. R. Tolkien', 'J. Tolkien'),
        ], transform=lambda x: (x.name, x.same_name), ordered=False)
