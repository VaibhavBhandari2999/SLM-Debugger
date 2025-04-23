from django.db.models import IntegerField, Value
from django.db.models.functions import Left, Lower
from django.test import TestCase

from ..models import Author


class LeftTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Author.objects.create(name="John Smith", alias="smithj")
        Author.objects.create(name="Rhonda")

    def test_basic(self):
        """
        Tests the functionality of the `annotate` method with the `Left` function from Django's F expressions.
        
        This test function performs the following operations:
        1. Annotates the `Author` model with a new field `name_part` that contains the first 5 characters of the `name` field.
        2. Orders the annotated queryset by the `name` field and asserts that the resulting names are as expected.
        3. Updates the `alias` field for authors where `alias` is null,
        """

        authors = Author.objects.annotate(name_part=Left("name", 5))
        self.assertQuerySetEqual(
            authors.order_by("name"), ["John ", "Rhond"], lambda a: a.name_part
        )
        # If alias is null, set it to the first 2 lower characters of the name.
        Author.objects.filter(alias__isnull=True).update(alias=Lower(Left("name", 2)))
        self.assertQuerySetEqual(
            authors.order_by("name"), ["smithj", "rh"], lambda a: a.alias
        )

    def test_invalid_length(self):
        with self.assertRaisesMessage(ValueError, "'length' must be greater than 0"):
            Author.objects.annotate(raises=Left("name", 0))

    def test_expressions(self):
        """
        Tests the functionality of the `annotate` method in Django ORM by creating an `Author` queryset. The queryset is annotated with a `name_part` field, which is the leftmost 3 characters of the `name` field. The test then orders the queryset by the `name` field and asserts that the `name_part` values are equal to 'Joh' and 'Rho' respectively.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Attributes:
        - `authors`: A
        """

        authors = Author.objects.annotate(
            name_part=Left("name", Value(3, output_field=IntegerField()))
        )
        self.assertQuerySetEqual(
            authors.order_by("name"), ["Joh", "Rho"], lambda a: a.name_part
        )
