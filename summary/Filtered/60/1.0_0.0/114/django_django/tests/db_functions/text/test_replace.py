from django.db.models import F, Value
from django.db.models.functions import Concat, Replace
from django.test import TestCase

from ..models import Author


class ReplaceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Author.objects.create(name="George R. R. Martin")
        Author.objects.create(name="J. R. R. Tolkien")

    def test_replace_with_empty_string(self):
        """
        Tests the `Replace` function by replacing the middle name in the author's name with an empty string.
        
        Args:
        None
        
        Returns:
        None
        
        Key Parameters:
        - `qs`: An annotated queryset of `Author` objects. Each object has an additional field `without_middlename` which is the result of replacing "R. R. " with an empty string in the original `name` field.
        
        Example Usage:
        >>> test_replace_with_empty_string()
        This will run the
        """

        qs = Author.objects.annotate(
            without_middlename=Replace(F("name"), Value("R. R. "), Value("")),
        )
        self.assertQuerySetEqual(
            qs,
            [
                ("George R. R. Martin", "George Martin"),
                ("J. R. R. Tolkien", "J. Tolkien"),
            ],
            transform=lambda x: (x.name, x.without_middlename),
            ordered=False,
        )

    def test_case_sensitive(self):
        qs = Author.objects.annotate(
            same_name=Replace(F("name"), Value("r. r."), Value(""))
        )
        self.assertQuerySetEqual(
            qs,
            [
                ("George R. R. Martin", "George R. R. Martin"),
                ("J. R. R. Tolkien", "J. R. R. Tolkien"),
            ],
            transform=lambda x: (x.name, x.same_name),
            ordered=False,
        )

    def test_replace_expression(self):
        qs = Author.objects.annotate(
            same_name=Replace(
                Concat(Value("Author: "), F("name")), Value("Author: "), Value("")
            ),
        )
        self.assertQuerySetEqual(
            qs,
            [
                ("George R. R. Martin", "George R. R. Martin"),
                ("J. R. R. Tolkien", "J. R. R. Tolkien"),
            ],
            transform=lambda x: (x.name, x.same_name),
            ordered=False,
        )

    def test_update(self):
        Author.objects.update(
            name=Replace(F("name"), Value("R. R. "), Value("")),
        )
        self.assertQuerySetEqual(
            Author.objects.all(),
            [
                ("George Martin"),
                ("J. Tolkien"),
            ],
            transform=lambda x: x.name,
            ordered=False,
        )

    def test_replace_with_default_arg(self):
        """
        Tests the `Replace` function with a default replacement argument.
        
        This function tests the `Replace` function from Django's F expressions. The `Replace` function is used to replace a specified substring in a field value. By default, the replacement is an empty string, effectively removing the specified substring.
        
        Parameters:
        None
        
        Returns:
        None
        
        Example Usage:
        The default replacement is an empty string. The function creates an annotated queryset that replaces the substring "R. R. " in the '
        """

        # The default replacement is an empty string.
        qs = Author.objects.annotate(same_name=Replace(F("name"), Value("R. R. ")))
        self.assertQuerySetEqual(
            qs,
            [
                ("George R. R. Martin", "George Martin"),
                ("J. R. R. Tolkien", "J. Tolkien"),
            ],
            transform=lambda x: (x.name, x.same_name),
            ordered=False,
        )
