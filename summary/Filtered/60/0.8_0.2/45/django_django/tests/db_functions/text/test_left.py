from django.db.models import CharField, Value
from django.db.models.functions import Left, Lower
from django.test import TestCase

from ..models import Author


class LeftTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda')

    def test_basic(self):
        """
        Tests the functionality of the `annotate` method with `Left` and `Lower` functions.
        
        This test case checks the behavior of the `annotate` method when used with the `Left` function to extract a part of the `name` field. It also verifies the update of the `alias` field based on the first two lowercase characters of the `name` field for records where `alias` is `NULL`.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        1. The queryset
        """

        authors = Author.objects.annotate(name_part=Left('name', 5))
        self.assertQuerysetEqual(authors.order_by('name'), ['John ', 'Rhond'], lambda a: a.name_part)
        # If alias is null, set it to the first 2 lower characters of the name.
        Author.objects.filter(alias__isnull=True).update(alias=Lower(Left('name', 2)))
        self.assertQuerysetEqual(authors.order_by('name'), ['smithj', 'rh'], lambda a: a.alias)

    def test_invalid_length(self):
        with self.assertRaisesMessage(ValueError, "'length' must be greater than 0"):
            Author.objects.annotate(raises=Left('name', 0))

    def test_expressions(self):
        authors = Author.objects.annotate(name_part=Left('name', Value(3), output_field=CharField()))
        self.assertQuerysetEqual(authors.order_by('name'), ['Joh', 'Rho'], lambda a: a.name_part)
