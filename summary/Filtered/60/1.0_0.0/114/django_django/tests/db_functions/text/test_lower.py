from django.db.models import CharField
from django.db.models.functions import Lower
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class LowerTests(TestCase):
    def test_basic(self):
        """
        Tests the basic functionality of the Author model and its methods.
        
        This test function creates two Author objects with different names and aliases. It then annotates the queryset with the lowercased name and orders it by the name field. The function asserts that the queryset is ordered correctly and that the names are lowercased. After updating the names to their lowercase versions, it asserts that the names in the queryset match the updated lowercase names.
        
        Key Parameters:
        - None
        
        Keywords:
        - None
        
        Input:
        - None
        """

        Author.objects.create(name="John Smith", alias="smithj")
        Author.objects.create(name="Rhonda")
        authors = Author.objects.annotate(lower_name=Lower("name"))
        self.assertQuerySetEqual(
            authors.order_by("name"), ["john smith", "rhonda"], lambda a: a.lower_name
        )
        Author.objects.update(name=Lower("name"))
        self.assertQuerySetEqual(
            authors.order_by("name"),
            [
                ("john smith", "john smith"),
                ("rhonda", "rhonda"),
            ],
            lambda a: (a.lower_name, a.name),
        )

    def test_num_args(self):
        """
        Tests the behavior of the `Lower` function when used with the `update` method of the `Author` model's manager.
        
        This function checks if the `Lower` function raises a `TypeError` when an incorrect number of arguments are provided. Specifically, it expects the `Lower` function to take exactly one argument but receives two arguments ("name" and "name").
        
        Parameters:
        None
        
        Raises:
        TypeError: If the `Lower` function is called with the correct number of arguments, no
        """

        with self.assertRaisesMessage(
            TypeError, "'Lower' takes exactly 1 argument (2 given)"
        ):
            Author.objects.update(name=Lower("name", "name"))

    def test_transform(self):
        with register_lookup(CharField, Lower):
            Author.objects.create(name="John Smith", alias="smithj")
            Author.objects.create(name="Rhonda")
            authors = Author.objects.filter(name__lower__exact="john smith")
            self.assertQuerySetEqual(
                authors.order_by("name"), ["John Smith"], lambda a: a.name
            )
