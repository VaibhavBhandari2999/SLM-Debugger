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
        setUpTestData(cls):
        A class method for setting up test data for the class. This method is used to create and store test data that will be reused across multiple test methods.
        
        Parameters:
        cls (cls): The class object on which the method is called. This is used to create class-level test data.
        
        Returns:
        None: This method does not return any value. It creates and stores test data as class attributes for use in test methods.
        
        Example Usage:
        This method is typically
        """

        cls.john = Author.objects.create(name='John Smith', alias='smithj')
        cls.elena = Author.objects.create(name='Élena Jordan', alias='elena')
        cls.python = Author.objects.create(name='パイソン')

    def test_null(self):
        author = Author.objects.annotate(backward=Reverse('alias')).get(pk=self.python.pk)
        self.assertEqual(author.backward, '' if connection.features.interprets_empty_strings_as_nulls else None)

    def test_basic(self):
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
        Tests the functionality of custom lookups and expressions in Django ORM.
        
        This test function checks the behavior of custom lookups and expressions in Django ORM. It first annotates an author object with a reversed and trimmed name, then asserts that the reversed name is correctly calculated. It then registers two custom lookups for CharField: Reverse and Length. Using these lookups, it filters and excludes author objects based on the length of their reversed names and asserts the results.
        
        Key Parameters:
        - None
        
        Key Keywords
        """

        author = Author.objects.annotate(backward=Reverse(Trim('name'))).get(pk=self.john.pk)
        self.assertEqual(author.backward, self.john.name[::-1])
        with register_lookup(CharField, Reverse), register_lookup(CharField, Length):
            authors = Author.objects.all()
            self.assertCountEqual(authors.filter(name__reverse__length__gt=7), [self.john, self.elena])
            self.assertCountEqual(authors.exclude(name__reverse__length__gt=7), [self.python])
