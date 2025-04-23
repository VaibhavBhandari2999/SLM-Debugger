from django.db.models import IntegerField
from django.db.models.functions import Chr, Left, Ord
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class ChrTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls):
        A class method used to set up test data for a test case. This method is called once before any test method is run.
        
        Parameters:
        cls: The test class instance.
        
        Returns:
        None. This method populates the test class with predefined Author objects for testing purposes.
        
        Key Data Points:
        - Creates and saves three Author objects with different names and aliases.
        - 'john': name='John Smith', alias='smithj'
        - 'el
        """

        cls.john = Author.objects.create(name='John Smith', alias='smithj')
        cls.elena = Author.objects.create(name='Élena Jordan', alias='elena')
        cls.rhonda = Author.objects.create(name='Rhonda')

    def test_basic(self):
        authors = Author.objects.annotate(first_initial=Left('name', 1))
        self.assertCountEqual(authors.filter(first_initial=Chr(ord('J'))), [self.john])
        self.assertCountEqual(authors.exclude(first_initial=Chr(ord('J'))), [self.elena, self.rhonda])

    def test_non_ascii(self):
        authors = Author.objects.annotate(first_initial=Left('name', 1))
        self.assertCountEqual(authors.filter(first_initial=Chr(ord('É'))), [self.elena])
        self.assertCountEqual(authors.exclude(first_initial=Chr(ord('É'))), [self.john, self.rhonda])

    def test_transform(self):
        with register_lookup(IntegerField, Chr):
            authors = Author.objects.annotate(name_code_point=Ord('name'))
            self.assertCountEqual(authors.filter(name_code_point__chr=Chr(ord('J'))), [self.john])
            self.assertCountEqual(authors.exclude(name_code_point__chr=Chr(ord('J'))), [self.elena, self.rhonda])
