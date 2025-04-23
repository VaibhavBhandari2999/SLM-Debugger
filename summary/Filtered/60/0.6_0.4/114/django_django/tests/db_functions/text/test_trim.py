from django.db.models import CharField
from django.db.models.functions import LTrim, RTrim, Trim
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class TrimTests(TestCase):
    def test_trim(self):
        """
        Test the trimming functionality for the Author model.
        
        This test function checks the trimming functionality for the `name` field of the Author model. It creates two Author objects with specific names and aliases, then annotates the queryset with LTrim, RTrim, and Trim functions to remove leading and trailing spaces from the `name` field. The test asserts that the trimmed values match the expected results.
        
        Parameters:
        - None (The test is based on the internal state of the database and does not require any
        """

        Author.objects.create(name="  John ", alias="j")
        Author.objects.create(name="Rhonda", alias="r")
        authors = Author.objects.annotate(
            ltrim=LTrim("name"),
            rtrim=RTrim("name"),
            trim=Trim("name"),
        )
        self.assertQuerySetEqual(
            authors.order_by("alias"),
            [
                ("John ", "  John", "John"),
                ("Rhonda", "Rhonda", "Rhonda"),
            ],
            lambda a: (a.ltrim, a.rtrim, a.trim),
        )

    def test_trim_transform(self):
        """
        Tests the functionality of different string trim transformations (LTrim, RTrim, and Trim) on the 'name' field of the Author model.
        
        Key Parameters:
        - `transform`: The string transformation function to be tested (LTrim, RTrim, or Trim).
        - `trimmed_name`: The expected trimmed name after applying the transformation.
        
        Input:
        - A list of test cases, each containing a transformation function and the expected trimmed name.
        - An Author model instance with a name field containing leading and trailing
        """

        Author.objects.create(name=" John  ")
        Author.objects.create(name="Rhonda")
        tests = (
            (LTrim, "John  "),
            (RTrim, " John"),
            (Trim, "John"),
        )
        for transform, trimmed_name in tests:
            with self.subTest(transform=transform):
                with register_lookup(CharField, transform):
                    authors = Author.objects.filter(
                        **{"name__%s" % transform.lookup_name: trimmed_name}
                    )
                    self.assertQuerySetEqual(authors, [" John  "], lambda a: a.name)
