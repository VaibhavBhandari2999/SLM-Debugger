from django.db.models import F, IntegerField
from django.db.models.functions import Chr, Left, Ord
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class ChrTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.john = Author.objects.create(name="John Smith", alias="smithj")
        cls.elena = Author.objects.create(name="Élena Jordan", alias="elena")
        cls.rhonda = Author.objects.create(name="Rhonda")

    def test_basic(self):
        """
        Test the basic functionality of the Author model's annotation and filtering.
        
        This test function checks the functionality of the `annotate` method on the Author model, specifically using the `Left` function to extract the first initial of the author's name. It then filters the annotated queryset to find authors whose first initial matches a given character and those whose first initial does not match.
        
        Parameters:
        - None (the test relies on pre-defined author instances `self.john`, `self.elena`, and `self
        """

        authors = Author.objects.annotate(first_initial=Left("name", 1))
        self.assertCountEqual(authors.filter(first_initial=Chr(ord("J"))), [self.john])
        self.assertCountEqual(
            authors.exclude(first_initial=Chr(ord("J"))), [self.elena, self.rhonda]
        )

    def test_non_ascii(self):
        """
        Tests filtering and exclusion of authors based on their first initial, specifically using non-ASCII characters.
        
        This function asserts that the query filters correctly for authors whose first initial is 'É' and excludes those whose first initial is not 'É'. The filtering is done using the `annotate` method with the `Left` function to extract the first character of the author's name and the `Chr` function to convert the ASCII value to a character.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Assertions
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
