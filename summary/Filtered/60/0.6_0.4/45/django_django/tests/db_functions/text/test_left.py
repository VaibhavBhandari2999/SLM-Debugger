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
        Tests the functionality of the Author model's name and alias fields.
        
        This test function performs the following operations:
        1. Annotates the 'name' field of the Author model with the first 5 characters using the Left function.
        2. Orders the annotated queryset by the 'name' field and asserts that the first element is 'John ' and the second is 'Rhond'.
        3. Updates the 'alias' field for authors where 'alias' is null, setting it to the first 2
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
