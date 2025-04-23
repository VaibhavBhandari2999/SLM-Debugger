from django.db.models import CharField, Value
from django.db.models.functions import Left, Ord
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class OrdTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.john = Author.objects.create(name='John Smith', alias='smithj')
        cls.elena = Author.objects.create(name='Élena Jordan', alias='elena')
        cls.rhonda = Author.objects.create(name='Rhonda')

    def test_basic(self):
        """
        Tests the basic functionality of the `annotate` method with the `Ord` function.
        
        This function checks if the `annotate` method correctly applies the `Ord` function to the 'name' field of the `Author` model. It then verifies that filtering and exclusion operations using the annotated field ('name_part') work as expected.
        
        Parameters:
        - None (This function uses pre-defined instances `self.elena`, `self.rhonda`, and `self.john`).
        
        Returns:
        - None (
        """

        authors = Author.objects.annotate(name_part=Ord('name'))
        self.assertCountEqual(authors.filter(name_part__gt=Ord(Value('John'))), [self.elena, self.rhonda])
        self.assertCountEqual(authors.exclude(name_part__gt=Ord(Value('John'))), [self.john])

    def test_transform(self):
        with register_lookup(CharField, Ord):
            authors = Author.objects.annotate(first_initial=Left('name', 1))
            self.assertCountEqual(authors.filter(first_initial__ord=ord('J')), [self.john])
            self.assertCountEqual(authors.exclude(first_initial__ord=ord('J')), [self.elena, self.rhonda])
d('J')), [self.elena, self.rhonda])
