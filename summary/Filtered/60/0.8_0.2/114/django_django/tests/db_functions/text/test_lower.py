from django.db.models import CharField
from django.db.models.functions import Lower
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class LowerTests(TestCase):
    def test_basic(self):
        """
        Tests the basic functionality of updating and annotating Author objects in a Django model.
        
        This test function performs the following operations:
        1. Creates two Author objects with different names and aliases.
        2. Annotates the Author objects with a lower-cased version of their names.
        3. Orders the annotated objects by their names and checks if the lower-cased names match the expected values.
        4. Updates the names of the Author objects to their lower-cased versions.
        5. Orders the updated Author objects by
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
        Tests the behavior of the `Lower` function when used with the `update` method in Django ORM.
        
        This test checks that the `Lower` function raises a `TypeError` when more than one argument is provided. Specifically, it ensures that the `Lower` function only accepts one argument and that providing two arguments results in a type error with a specific message.
        
        Key Parameters:
        - None
        
        Key Keyword Arguments:
        - None
        
        Input:
        - The `Lower` function is called with two arguments: "
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
