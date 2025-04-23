from django.db import connection
from django.db.models import CharField
from django.db.models.functions import Length, Reverse, Trim
from django.test import TestCase
from django.test.utils import register_lookup

from ..models import Author


class ReverseTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.john = Author.objects.create(name="John Smith", alias="smithj")
        cls.elena = Author.objects.create(name="Élena Jordan", alias="elena")
        cls.python = Author.objects.create(name="パイソン")

    def test_null(self):
        author = Author.objects.annotate(backward=Reverse("alias")).get(
            pk=self.python.pk
        )
        self.assertEqual(
            author.backward,
            "" if connection.features.interprets_empty_strings_as_nulls else None,
        )

    def test_basic(self):
        """
        Tests the functionality of the `Reverse` lookup in the `annotate` method.
        
        This test checks if the `Reverse` lookup correctly reverses the characters in the `name` field of the `Author` model. The `annotate` method is used to add a new field `backward` to each author object, which contains the reversed version of their name. The test asserts that the resulting queryset matches the expected output, which includes tuples of the original name and its reversed version. The `ordered=False
        """

        authors = Author.objects.annotate(backward=Reverse("name"))
        self.assertQuerySetEqual(
            authors,
            [
                ("John Smith", "htimS nhoJ"),
                ("Élena Jordan", "nadroJ anelÉ"),
                ("パイソン", "ンソイパ"),
            ],
            lambda a: (a.name, a.backward),
            ordered=False,
        )

    def test_transform(self):
        with register_lookup(CharField, Reverse):
            authors = Author.objects.all()
            self.assertCountEqual(
                authors.filter(name__reverse=self.john.name[::-1]), [self.john]
            )
            self.assertCountEqual(
                authors.exclude(name__reverse=self.john.name[::-1]),
                [self.elena, self.python],
            )

    def test_expressions(self):
        """
        Tests for expressions in Django ORM.
        
        This function tests the usage of custom expressions in Django ORM queries. It includes tests for the `Reverse` and `Length` lookups.
        
        Parameters:
        - self: The test case instance.
        
        Key Methods:
        1. `test_expressions`: Tests the `Reverse` and `Length` lookups.
        - `Reverse`: Reverses the string of the `name` field.
        - `Length`: Determines the length of the reversed string.
        - The
        """

        author = Author.objects.annotate(backward=Reverse(Trim("name"))).get(
            pk=self.john.pk
        )
        self.assertEqual(author.backward, self.john.name[::-1])
        with register_lookup(CharField, Reverse), register_lookup(CharField, Length):
            authors = Author.objects.all()
            self.assertCountEqual(
                authors.filter(name__reverse__length__gt=7), [self.john, self.elena]
            )
            self.assertCountEqual(
                authors.exclude(name__reverse__length__gt=7), [self.python]
            )
elf.assertCountEqual(
                authors.exclude(name__reverse__length__gt=7), [self.python]
            )
