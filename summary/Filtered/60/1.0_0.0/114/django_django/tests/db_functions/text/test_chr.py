from django.db.models import F, IntegerField
from django.db.models.functions import Chr, Left, Ord
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class ChrTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData is a class method used to set up test data for a Django test case. It is called once before any tests are run and is used to create test data that can be shared across multiple test methods.
        
        Parameters:
        - cls: The test class itself, used to create and access test data.
        
        Returns:
        - None: This method does not return any value. It is used to create and store test data in the class for later use in test methods.
        
        Key Points:
        - The method
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
        """
        Tests the annotate method of the Author model.
        
        This function checks if the annotate method correctly adds the first_initial and initial_chr fields to the query. It then filters the results to find authors whose first_initial matches the initial_chr.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The filtered result should contain only the author 'john'.
        - The first_initial field should be the leftmost character of the name.
        - The initial_chr field should be the character 'J' converted
        """

        authors = Author.objects.annotate(
            first_initial=Left("name", 1),
            initial_chr=Chr(ord("J")),
        )
        self.assertSequenceEqual(
            authors.filter(first_initial=F("initial_chr")),
            [self.john],
        )
