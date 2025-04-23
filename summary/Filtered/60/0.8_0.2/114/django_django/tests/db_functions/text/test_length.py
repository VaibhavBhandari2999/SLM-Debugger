from django.db.models import CharField
from django.db.models.functions import Length
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class LengthTests(TestCase):
    def test_basic(self):
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
        
        This function creates three author entries in the database and then queries them using the `order_by` method with the `Length` function to sort by the length of the name and alias. The expected order is determined by the length of the name and alias, with shorter entries appearing first.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - Creates three author objects with different names and aliases.
        - Orders
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
        
        This method registers a custom lookup for CharField and creates two instances of Author with different names. It then filters the Author objects where the length of the name is greater than 7 characters. The result is ordered by name and compared to the expected output.
        
        Key Parameters:
        - None
        
        Keywords:
        - register_lookup: Registers the Length lookup for CharField.
        - Author.objects.create: Creates instances of the Author model.
        - filter: Filters the
        """

        with register_lookup(CharField, Length):
            Author.objects.create(name="John Smith", alias="smithj")
            Author.objects.create(name="Rhonda")
            authors = Author.objects.filter(name__length__gt=7)
            self.assertQuerySetEqual(
                authors.order_by("name"), ["John Smith"], lambda a: a.name
            )
