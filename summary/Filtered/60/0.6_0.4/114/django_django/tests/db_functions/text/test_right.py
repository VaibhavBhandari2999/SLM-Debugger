from django.db.models import IntegerField, Value
from django.db.models.functions import Lower, Right
from django.test import TestCase

from ..models import Author


class RightTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Author.objects.create(name="John Smith", alias="smithj")
        Author.objects.create(name="Rhonda")

    def test_basic(self):
        """
        Tests the functionality of the `Author` model's `name` field with custom annotations and updates.
        
        This test function performs the following operations:
        1. Annotates the `Author` model with a new field `name_part` which is the last 5 characters of the `name` field.
        2. Orders the annotated queryset by the `name` field and checks if the `name_part` values match the expected output `["Smith", "honda"]`.
        3. Updates the `alias
        """

        authors = Author.objects.annotate(name_part=Right("name", 5))
        self.assertQuerySetEqual(
            authors.order_by("name"), ["Smith", "honda"], lambda a: a.name_part
        )
        # If alias is null, set it to the first 2 lower characters of the name.
        Author.objects.filter(alias__isnull=True).update(alias=Lower(Right("name", 2)))
        self.assertQuerySetEqual(
            authors.order_by("name"), ["smithj", "da"], lambda a: a.alias
        )

    def test_invalid_length(self):
        with self.assertRaisesMessage(ValueError, "'length' must be greater than 0"):
            Author.objects.annotate(raises=Right("name", 0))

    def test_expressions(self):
        authors = Author.objects.annotate(
            name_part=Right("name", Value(3, output_field=IntegerField()))
        )
        self.assertQuerySetEqual(
            authors.order_by("name"), ["ith", "nda"], lambda a: a.name_part
        )
       authors.order_by("name"), ["ith", "nda"], lambda a: a.name_part
        )
