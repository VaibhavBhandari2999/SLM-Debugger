from django.db.models import CharField, Value
from django.db.models.functions import Left, Ord
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class OrdTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        ------------------
        This method is a class method used to set up test data for a test case. It is called once before any test method in the class is run.
        
        Parameters:
        - cls: The class object for which the test data is being set up.
        
        Returns:
        - None: This method does not return any value. It creates and stores test data in the database.
        
        Key Data Points:
        - Creates and stores three instances of the Author model in the database:
        -
        """

        cls.john = Author.objects.create(name="John Smith", alias="smithj")
        cls.elena = Author.objects.create(name="Élena Jordan", alias="elena")
        cls.rhonda = Author.objects.create(name="Rhonda")

    def test_basic(self):
        """
        Test the basic functionality of the Author model's name ordering.
        
        This test function checks the ordering of author names using the Ord function. It creates a queryset of authors and annotates each with a part of the name for ordering purposes. The test then verifies that the authors whose names come after 'John' alphabetically are correctly identified, and those that do not are also correctly identified.
        
        Parameters:
        - None (the test relies on predefined author instances: self.elena, self.rhonda, and
        """

        authors = Author.objects.annotate(name_part=Ord("name"))
        self.assertCountEqual(
            authors.filter(name_part__gt=Ord(Value("John"))), [self.elena, self.rhonda]
        )
        self.assertCountEqual(
            authors.exclude(name_part__gt=Ord(Value("John"))), [self.john]
        )

    def test_transform(self):
        with register_lookup(CharField, Ord):
            authors = Author.objects.annotate(first_initial=Left("name", 1))
            self.assertCountEqual(
                authors.filter(first_initial__ord=ord("J")), [self.john]
            )
            self.assertCountEqual(
                authors.exclude(first_initial__ord=ord("J")), [self.elena, self.rhonda]
            )
