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
        authors = Author.objects.annotate(first_initial=Left('name', 1))
        self.assertCountEqual(authors.filter(first_initial=Chr(ord('J'))), [self.john])
        self.assertCountEqual(authors.exclude(first_initial=Chr(ord('J'))), [self.elena, self.rhonda])

    def test_non_ascii(self):
        """
        Tests the functionality of filtering authors based on their first initial using non-ASCII characters.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Operations:
        - Filters authors based on their first initial using the `Left` function to extract the first character of their name.
        - Uses `Chr` to convert ASCII values to characters for comparison.
        - Compares the filtered results with expected authors using `assertCountEqual`.
        
        Key Points:
        - The function tests the filtering of authors with non
        """

        authors = Author.objects.annotate(first_initial=Left('name', 1))
        self.assertCountEqual(authors.filter(first_initial=Chr(ord('É'))), [self.elena])
        self.assertCountEqual(authors.exclude(first_initial=Chr(ord('É'))), [self.john, self.rhonda])

    def test_transform(self):
        """
        Tests the transformation of a string field to its Unicode code point and back using custom lookups.
        
        This function registers a custom lookup `Chr` for `IntegerField` to convert Unicode code points to characters. It then performs the following tests:
        1. Filters `Author` objects where the `name` field's Unicode code point matches a specific character's code point.
        2. Filters `Author` objects where the `name` field's Unicode code point does not match a specific character's code point.
        
        Parameters
        """

        with register_lookup(IntegerField, Chr):
            authors = Author.objects.annotate(name_code_point=Ord('name'))
            self.assertCountEqual(authors.filter(name_code_point__chr=Chr(ord('J'))), [self.john])
            self.assertCountEqual(authors.exclude(name_code_point__chr=Chr(ord('J'))), [self.elena, self.rhonda])
