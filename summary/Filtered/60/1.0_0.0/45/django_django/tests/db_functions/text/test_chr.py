from django.db.models import IntegerField
from django.db.models.functions import Chr, Left, Ord
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class ChrTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.john = Author.objects.create(name='John Smith', alias='smithj')
        cls.elena = Author.objects.create(name='Élena Jordan', alias='elena')
        cls.rhonda = Author.objects.create(name='Rhonda')

    def test_basic(self):
        """
        Tests the basic functionality of the `annotate` method in Django ORM.
        
        This function checks the ability of the `annotate` method to extract the first initial of an author's name and filter based on that initial.
        
        Parameters:
        self (unittest.TestCase): The test case object for running assertions.
        
        Returns:
        None: This function does not return any value. It asserts the correctness of the query results.
        
        Key Points:
        - The `annotate` method is used to add a new field to each object in
        """

        authors = Author.objects.annotate(first_initial=Left('name', 1))
        self.assertCountEqual(authors.filter(first_initial=Chr(ord('J'))), [self.john])
        self.assertCountEqual(authors.exclude(first_initial=Chr(ord('J'))), [self.elena, self.rhonda])

    def test_non_ascii(self):
        authors = Author.objects.annotate(first_initial=Left('name', 1))
        self.assertCountEqual(authors.filter(first_initial=Chr(ord('É'))), [self.elena])
        self.assertCountEqual(authors.exclude(first_initial=Chr(ord('É'))), [self.john, self.rhonda])

    def test_transform(self):
        """
        Tests the transformation of a string field to its Unicode code point and back.
        
        This function tests the functionality of converting a string field to its Unicode code point and then back to a character using custom lookup functions. It uses Django's ORM to annotate and filter the 'Author' model.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Registers a custom lookup function `Chr` for the `IntegerField` to convert a Unicode code point back to a character.
        2. Annotates
        """

        with register_lookup(IntegerField, Chr):
            authors = Author.objects.annotate(name_code_point=Ord('name'))
            self.assertCountEqual(authors.filter(name_code_point__chr=Chr(ord('J'))), [self.john])
            self.assertCountEqual(authors.exclude(name_code_point__chr=Chr(ord('J'))), [self.elena, self.rhonda])
