from django.db.models import F, IntegerField
from django.db.models.functions import Chr, Left, Ord
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class ChrTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData is a class method used in Django testing to set up test data that will be used across multiple test methods. It is a class-level method, meaning it is defined at the class level and can be accessed via the class itself.
        
        Parameters:
        - cls: The class object for which the test data is being set up. This parameter is automatically passed by Django and is used to access class attributes.
        
        Key Data Points:
        - Creates and saves multiple instances of the Author model with different names and
        """

        cls.john = Author.objects.create(name="John Smith", alias="smithj")
        cls.elena = Author.objects.create(name="Élena Jordan", alias="elena")
        cls.rhonda = Author.objects.create(name="Rhonda")

    def test_basic(self):
        authors = Author.objects.annotate(first_initial=Left("name", 1))
        self.assertCountEqual(authors.filter(first_initial=Chr(ord("J"))), [self.john])
        self.assertCountEqual(
            authors.exclude(first_initial=Chr(ord("J"))), [self.elena, self.rhonda]
        )

    def test_non_ascii(self):
        """
        Tests filtering and exclusion of authors based on their first initial using non-ASCII characters.
        
        This function tests the behavior of filtering and excluding authors based on their first initial, specifically using a non-ASCII character 'É'. The test uses the `annotate` method to extract the first initial of the author's name and then filters and excludes authors based on this initial.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The `annotate` method is used to create a new field `first
        """

        authors = Author.objects.annotate(first_initial=Left("name", 1))
        self.assertCountEqual(authors.filter(first_initial=Chr(ord("É"))), [self.elena])
        self.assertCountEqual(
            authors.exclude(first_initial=Chr(ord("É"))), [self.john, self.rhonda]
        )

    def test_transform(self):
        with register_lookup(IntegerField, Chr):
            authors = Author.objects.annotate(name_code_point=Ord("name"))
            self.assertCountEqual(
                authors.filter(name_code_point__chr=Chr(ord("J"))), [self.john]
            )
            self.assertCountEqual(
                authors.exclude(name_code_point__chr=Chr(ord("J"))),
                [self.elena, self.rhonda],
            )

    def test_annotate(self):
        authors = Author.objects.annotate(
            first_initial=Left("name", 1),
            initial_chr=Chr(ord("J")),
        )
        self.assertSequenceEqual(
            authors.filter(first_initial=F("initial_chr")),
            [self.john],
        )
