from django.db.models import CharField
from django.db.models.functions import Upper
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class UpperTests(TestCase):
    def test_basic(self):
        """
        Tests the basic functionality of the `annotate` method in Django ORM.
        
        This test case checks the following:
        - Creates two `Author` objects with different names.
        - Annotates the `Author` queryset with an upper-cased version of the name.
        - Orders the queryset by the original name and verifies the upper-cased names.
        - Updates the names to their upper-cased versions and verifies the updated values.
        
        Parameters:
        - None
        
        Returns:
        - None
        """

        Author.objects.create(name="John Smith", alias="smithj")
        Author.objects.create(name="Rhonda")
        authors = Author.objects.annotate(upper_name=Upper("name"))
        self.assertQuerySetEqual(
            authors.order_by("name"),
            [
                "JOHN SMITH",
                "RHONDA",
            ],
            lambda a: a.upper_name,
        )
        Author.objects.update(name=Upper("name"))
        self.assertQuerySetEqual(
            authors.order_by("name"),
            [
                ("JOHN SMITH", "JOHN SMITH"),
                ("RHONDA", "RHONDA"),
            ],
            lambda a: (a.upper_name, a.name),
        )

    def test_transform(self):
        """
        Tests the transformation functionality for the CharField using the Upper lookup.
        
        This function registers a custom lookup 'Upper' for the CharField, creates instances of the Author model with different names and aliases, and then filters the authors based on the transformed name. The results are then compared to the expected output.
        
        Key Parameters:
        - None
        
        Keywords:
        - register_lookup: Registers a custom lookup for the CharField.
        - CharField: The field type for which the custom lookup is registered.
        - Upper: The
        """

        with register_lookup(CharField, Upper):
            Author.objects.create(name="John Smith", alias="smithj")
            Author.objects.create(name="Rhonda")
            authors = Author.objects.filter(name__upper__exact="JOHN SMITH")
            self.assertQuerySetEqual(
                authors.order_by("name"),
                [
                    "John Smith",
                ],
                lambda a: a.name,
            )
