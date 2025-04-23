import datetime

from django.db import models
from django.test import TestCase
from django.test.utils import isolate_apps

from .models import InternationalArticle


class SimpleTests(TestCase):
    def test_international(self):
        """
        Test the functionality of the InternationalArticle model.
        
        This test function creates an instance of the InternationalArticle model with a specified headline and publication date. It then checks that the string representation of the created object matches the expected headline.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key elements:
        - InternationalArticle: The model being tested.
        - headline: The headline of the article (string).
        - pub_date: The publication date of the article (datetime).
        
        Example:
        >>> test_international
        """

        a = InternationalArticle.objects.create(
            headline="Girl wins €12.500 in lottery",
            pub_date=datetime.datetime(2005, 7, 28),
        )
        self.assertEqual(str(a), "Girl wins €12.500 in lottery")

    @isolate_apps("str")
    def test_defaults(self):
        """
        The default implementation of __str__ and __repr__ should return
        instances of str.
        """

        class Default(models.Model):
            pass

        obj = Default()
        # Explicit call to __str__/__repr__ to make sure str()/repr() don't
        # coerce the returned value.
        self.assertIsInstance(obj.__str__(), str)
        self.assertIsInstance(obj.__repr__(), str)
        self.assertEqual(str(obj), "Default object (None)")
        self.assertEqual(repr(obj), "<Default: Default object (None)>")
        obj2 = Default(pk=100)
        self.assertEqual(str(obj2), "Default object (100)")
        self.assertEqual(repr(obj2), "<Default: Default object (100)>")
