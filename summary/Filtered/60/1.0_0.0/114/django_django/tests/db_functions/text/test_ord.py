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
        This method is a class method used to set up test data for a test case. It is called once before any test method is run.
        
        Parameters:
        cls: The test class itself, used to create and store test data.
        
        Returns:
        None. This method populates the test class with test data (Author objects) for use in test methods.
        
        Example Usage:
        class AuthorTest(TestCase):
        @classmethod
        def setUpTestData(cls):
        cls.j
        """

        cls.john = Author.objects.create(name="John Smith", alias="smithj")
        cls.elena = Author.objects.create(name="Élena Jordan", alias="elena")
        cls.rhonda = Author.objects.create(name="Rhonda")

    def test_basic(self):
        authors = Author.objects.annotate(name_part=Ord("name"))
        self.assertCountEqual(
            authors.filter(name_part__gt=Ord(Value("John"))), [self.elena, self.rhonda]
        )
        self.assertCountEqual(
            authors.exclude(name_part__gt=Ord(Value("John"))), [self.john]
        )

    def test_transform(self):
        """
        Tests the transformation of a CharField using the Ord lookup.
        
        This function registers a custom lookup 'Ord' for the CharField and then performs
        annotations and filters on the Author model. It asserts that the filtered results
        match the expected authors based on the first initial character's ordinal value.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Registers the 'Ord' lookup for CharField.
        2. Annotates the 'name' field of the Author model with the first
        """

        with register_lookup(CharField, Ord):
            authors = Author.objects.annotate(first_initial=Left("name", 1))
            self.assertCountEqual(
                authors.filter(first_initial__ord=ord("J")), [self.john]
            )
            self.assertCountEqual(
                authors.exclude(first_initial__ord=ord("J")), [self.elena, self.rhonda]
            )
