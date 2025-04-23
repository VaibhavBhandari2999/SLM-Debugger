from django.db.models import CharField
from django.db.models.functions import Upper
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class UpperTests(TestCase):
    def test_basic(self):
        """
        Tests the basic functionality of the `annotate` method in Django ORM.
        
        This test creates two instances of the `Author` model with different names. It then annotates the query set with an upper-cased version of the name field. The test checks if the annotated names are correctly upper-cased and ordered by the original name field. After updating the name field to its upper-cased version, the test verifies that the names in the query set match the updated values.
        
        Key Parameters:
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
