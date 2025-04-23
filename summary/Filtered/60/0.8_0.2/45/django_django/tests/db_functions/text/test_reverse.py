from django.db import connection
from django.db.models import CharField
from django.db.models.functions import Length, Reverse, Trim
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class ReverseTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData class method is used to set up test data for a test class. It creates and saves test data that can be reused across multiple test methods.
        
        Parameters:
        cls (cls): The test class instance.
        
        Returns:
        None
        
        Key Data Points:
        - Creates and saves three Author objects with different names and aliases.
        - The first author is named 'John Smith' with an alias 'smithj'.
        - The second author is named 'Élena Jordan' with an alias 'el
        """

        cls.john = Author.objects.create(name='John Smith', alias='smithj')
        cls.elena = Author.objects.create(name='Élena Jordan', alias='elena')
        cls.python = Author.objects.create(name='パイソン')

    def test_null(self):
        author = Author.objects.annotate(backward=Reverse('alias')).get(pk=self.python.pk)
        self.assertEqual(author.backward, '' if connection.features.interprets_empty_strings_as_nulls else None)

    def test_basic(self):
        """
        Tests the basic functionality of the `Reverse` lookup.
        
        This test checks if the `Reverse` lookup correctly reverses the characters in the 'name' field of the Author model. The test creates an annotated queryset of authors with their names reversed and compares it against a list of expected tuples, where each tuple contains the original name and its reversed version.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - The queryset of authors with reversed names is compared against a list of expected tuples, ensuring
        """

        authors = Author.objects.annotate(backward=Reverse('name'))
        self.assertQuerysetEqual(
            authors,
            [
                ('John Smith', 'htimS nhoJ'),
                ('Élena Jordan', 'nadroJ anelÉ'),
                ('パイソン', 'ンソイパ'),
            ],
            lambda a: (a.name, a.backward),
            ordered=False,
        )

    def test_transform(self):
        with register_lookup(CharField, Reverse):
            authors = Author.objects.all()
            self.assertCountEqual(authors.filter(name__reverse=self.john.name[::-1]), [self.john])
            self.assertCountEqual(authors.exclude(name__reverse=self.john.name[::-1]), [self.elena, self.python])

    def test_expressions(self):
        """
        Tests for the expressions functionality in the Author model.
        
        This function tests the usage of custom lookups and expressions in Django queries. It includes the following key steps:
        - Annotates an Author object with a reversed and trimmed name.
        - Asserts that the reversed and trimmed name matches the expected value.
        - Registers custom lookups for the CharField.
        - Filters and asserts the results based on the custom reverse and length lookups.
        
        Parameters:
        self: The current test case instance.
        
        Returns:
        """

        author = Author.objects.annotate(backward=Reverse(Trim('name'))).get(pk=self.john.pk)
        self.assertEqual(author.backward, self.john.name[::-1])
        with register_lookup(CharField, Reverse), register_lookup(CharField, Length):
            authors = Author.objects.all()
            self.assertCountEqual(authors.filter(name__reverse__length__gt=7), [self.john, self.elena])
            self.assertCountEqual(authors.exclude(name__reverse__length__gt=7), [self.python])
