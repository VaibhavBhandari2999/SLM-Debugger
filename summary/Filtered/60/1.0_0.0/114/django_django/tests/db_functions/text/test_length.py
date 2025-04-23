from django.db.models import CharField
from django.db.models.functions import Length
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class LengthTests(TestCase):
    def test_basic(self):
        """
        Tests the functionality of the `annotate` method with the `Length` function from Django's ORM.
        
        This test creates two `Author` objects and then uses the `annotate` method to add two new fields to the query set: `name_length` and `alias_length`. The `name_length` field is the length of the `name` field, and the `alias_length` field is the length of the `alias` field. The test then checks if the query set is ordered correctly and
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
        
        This function creates three author objects with specific names and aliases, then orders them by the length of their names and aliases. It asserts that the resulting queryset matches the expected order.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Elements:
        - Author: A model representing an author with name and alias fields.
        - Length: A function used to calculate the length of the name and alias fields.
        - order_by
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
        """
        Tests the transformation of a CharField using the Length lookup.
        
        This test registers a custom lookup `Length` for the `CharField` and creates two instances of the `Author` model. It then filters the authors based on the length of their names and asserts that the filtered queryset contains the expected name.
        
        Key Parameters:
        - None
        
        Keywords:
        - register_lookup: Registers the `Length` lookup for the `CharField`.
        - CharField: The character field type for the model.
        - Length:
        """

        with register_lookup(CharField, Length):
            Author.objects.create(name="John Smith", alias="smithj")
            Author.objects.create(name="Rhonda")
            authors = Author.objects.filter(name__length__gt=7)
            self.assertQuerySetEqual(
                authors.order_by("name"), ["John Smith"], lambda a: a.name
            )
