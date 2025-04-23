from django.db.models import CharField
from django.db.models.functions import Length
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class LengthTests(TestCase):
    def test_basic(self):
        """
        Tests the basic functionality of the `annotate` method with the `Length` function.
        
        This test creates two `Author` objects and then uses the `annotate` method to add two new fields to the query set: `name_length` and `alias_length`. These fields represent the lengths of the `name` and `alias` fields, respectively. The test then orders the resulting query set by the `name` field and asserts that the expected values are returned. Additionally, it filters the query set
        """

        Author.objects.create(name="John Smith", alias="smithj")
        Author.objects.create(name="Rhonda")
        authors = Author.objects.annotate(
            name_length=Length("name"),
            alias_length=Length("alias"),
        )
        self.assertQuerySetEqual(
            authors.order_by("name"),
            [(10, 6), (6, None)],
            lambda a: (a.name_length, a.alias_length),
        )
        self.assertEqual(authors.filter(alias_length__lte=Length("name")).count(), 1)

    def test_ordering(self):
        """
        Tests the ordering of authors based on the length of their name and alias.
        
        This function creates three author objects with different names and aliases. It then orders the authors first by the length of their name and then by the length of their alias. The expected order is determined and compared against the actual order returned by the database query.
        
        Key Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - The order of the authors returned by the query matches the expected order based on the length of their name and
        """

        Author.objects.create(name="John Smith", alias="smithj")
        Author.objects.create(name="John Smith", alias="smithj1")
        Author.objects.create(name="Rhonda", alias="ronny")
        authors = Author.objects.order_by(Length("name"), Length("alias"))
        self.assertQuerySetEqual(
            authors,
            [
                ("Rhonda", "ronny"),
                ("John Smith", "smithj"),
                ("John Smith", "smithj1"),
            ],
            lambda a: (a.name, a.alias),
        )

    def test_transform(self):
        with register_lookup(CharField, Length):
            Author.objects.create(name="John Smith", alias="smithj")
            Author.objects.create(name="Rhonda")
            authors = Author.objects.filter(name__length__gt=7)
            self.assertQuerySetEqual(
                authors.order_by("name"), ["John Smith"], lambda a: a.name
            )
