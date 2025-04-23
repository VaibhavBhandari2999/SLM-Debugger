from django.db.models import CharField
from django.db.models.functions import Upper
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class UpperTests(TestCase):
    def test_basic(self):
        """
        Tests the basic functionality of the `Upper` function in Django ORM.
        
        This test function creates two `Author` objects with different names, annotates the queryset with the uppercased name, and then verifies the results. It first checks the uppercased names in ascending order by name, and then updates the names to their uppercased versions, verifying the updated names.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Inputs:
        - None
        
        Outputs:
        - The function asserts that the queryset of `
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
        Tests the transformation of a CharField using the Upper lookup.
        
        This test registers a custom lookup 'Upper' for CharField and creates two instances of the Author model with different names. It then filters the Author objects where the 'name' field, transformed to uppercase, is exactly 'JOHN SMITH'. The test asserts that the filtered queryset, when ordered by 'name', contains only the author with the name 'John Smith'.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Points:
        -
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
