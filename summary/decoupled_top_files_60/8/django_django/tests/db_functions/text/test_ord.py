from django.db.models import CharField, Value
from django.db.models.functions import Left, Ord
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class OrdTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData is a class method used for setting up test data for a Django test case. It is executed once before any test method is run, making it ideal for creating test fixtures.
        
        Parameters:
        cls: The class object for the test case. This is used to create and store the test data.
        
        Returns:
        None
        
        Key Data Points:
        - Creates and stores test data in the database using Django's ORM.
        - Creates three Author objects with different names and aliases.
        - The first author
        """

        cls.john = Author.objects.create(name='John Smith', alias='smithj')
        cls.elena = Author.objects.create(name='Élena Jordan', alias='elena')
        cls.rhonda = Author.objects.create(name='Rhonda')

    def test_basic(self):
        authors = Author.objects.annotate(name_part=Ord('name'))
        self.assertCountEqual(authors.filter(name_part__gt=Ord(Value('John'))), [self.elena, self.rhonda])
        self.assertCountEqual(authors.exclude(name_part__gt=Ord(Value('John'))), [self.john])

    def test_transform(self):
        """
        Tests the transformation of a CharField using the Ord lookup.
        
        This function registers a custom lookup 'Ord' for the CharField, then performs the following operations:
        1. Annotates the 'name' field of the Author model with the first initial using the Left function.
        2. Filters the annotated queryset to find authors whose first initial's ordinal value is equal to the ordinal value of 'J'.
        3. Filters the annotated queryset to find authors whose first initial's ordinal value is not equal to the
        """

        with register_lookup(CharField, Ord):
            authors = Author.objects.annotate(first_initial=Left('name', 1))
            self.assertCountEqual(authors.filter(first_initial__ord=ord('J')), [self.john])
            self.assertCountEqual(authors.exclude(first_initial__ord=ord('J')), [self.elena, self.rhonda])
