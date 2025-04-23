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
        """
        Tests the `Replace` function in Django ORM.
        
        This function creates an annotated queryset where each `Author` object's `name` field is modified by removing the prefix "Author: " using the `Replace` function. The `Concat` function is used to concatenate the prefix with the `name` field, and then `Replace` is used to strip the prefix. The resulting queryset is then compared to a list of expected tuples, each containing the original name and the modified name.
        
        Parameters:
        -
        """

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
jects.all(),
            [
                ("George Martin"),
                ("J. Tolkien"),
            ],
            transform=lambda x: x.name,
            ordered=False,
        )

    def test_replace_with_default_arg(self):
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
