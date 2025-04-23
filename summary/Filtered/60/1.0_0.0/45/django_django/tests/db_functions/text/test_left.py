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
        Tests basic usage of the `annotate` method in Django ORM.
        
        This test function checks the functionality of the `annotate` method by creating an annotation `name_part` which is the first 5 characters of the `name` field in the `Author` model. It then orders the queryset by the `name` field and asserts that the `name_part` matches the expected values 'John ' and 'Rhond'. After that, it updates the `alias` field for authors where `alias`
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
