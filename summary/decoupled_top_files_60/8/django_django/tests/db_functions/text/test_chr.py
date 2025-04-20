from django.db.models import IntegerField
from django.db.models.functions import Chr, Left, Ord
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class ChrTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        -------------------
        A class method that sets up test data for the entire test class. This method is used to create and store test data that will be reused across multiple test methods.
        
        Parameters:
        - cls: The test class itself, used to access class attributes and methods.
        
        Returns:
        - None: This method does not return anything, but it populates class attributes with test data.
        
        Key Data Points:
        - Creates and stores three instances of the Author model:
        - john:
        """

        cls.john = Author.objects.create(name='John Smith', alias='smithj')
        cls.elena = Author.objects.create(name='Élena Jordan', alias='elena')
        cls.rhonda = Author.objects.create(name='Rhonda')

    def test_basic(self):
        authors = Author.objects.annotate(first_initial=Left('name', 1))
        self.assertCountEqual(authors.filter(first_initial=Chr(ord('J'))), [self.john])
        self.assertCountEqual(authors.exclude(first_initial=Chr(ord('J'))), [self.elena, self.rhonda])

    def test_non_ascii(self):
        """
        Tests filtering of authors based on their first initial, specifically for non-ASCII characters.
        
        This function tests the filtering of authors based on their first initial using the `annotate` and `filter` methods of the Django ORM. It focuses on handling non-ASCII characters, such as 'É'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Methods:
        - `annotate(first_initial=Left('name', 1))`: Annotates each author with their first initial.
        - `filter
        """

        authors = Author.objects.annotate(first_initial=Left('name', 1))
        self.assertCountEqual(authors.filter(first_initial=Chr(ord('É'))), [self.elena])
        self.assertCountEqual(authors.exclude(first_initial=Chr(ord('É'))), [self.john, self.rhonda])

    def test_transform(self):
        with register_lookup(IntegerField, Chr):
            authors = Author.objects.annotate(name_code_point=Ord('name'))
            self.assertCountEqual(authors.filter(name_code_point__chr=Chr(ord('J'))), [self.john])
            self.assertCountEqual(authors.exclude(name_code_point__chr=Chr(ord('J'))), [self.elena, self.rhonda])
