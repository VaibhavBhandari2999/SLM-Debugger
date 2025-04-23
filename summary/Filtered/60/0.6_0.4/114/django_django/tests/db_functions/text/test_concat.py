from unittest import skipUnless

from django.db import connection
from django.db.models import CharField, TextField
from django.db.models import Value as V
from django.db.models.functions import Concat, ConcatPair, Upper
from django.test import TestCase
from django.utils import timezone

from ..models import Article, Author

lorem_ipsum = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua."""


class ConcatTests(TestCase):
    def test_basic(self):
        """
        Tests the basic functionality of the Author model's annotation and ordering.
        
        This test creates four Author objects with different names, aliases, and goes_by fields. It then annotates the query set with a concatenated string of the alias and goes_by fields. The test asserts that the resulting query set, when ordered by name, matches the expected output.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - A list of concatenated strings, ordered by the name field of
        """

        Author.objects.create(name="Jayden")
        Author.objects.create(name="John Smith", alias="smithj", goes_by="John")
        Author.objects.create(name="Margaret", goes_by="Maggie")
        Author.objects.create(name="Rhonda", alias="adnohR")
        authors = Author.objects.annotate(joined=Concat("alias", "goes_by"))
        self.assertQuerySetEqual(
            authors.order_by("name"),
            [
                "",
                "smithjJohn",
                "Maggie",
                "adnohR",
            ],
            lambda a: a.joined,
        )

    def test_gt_two_expressions(self):
        with self.assertRaisesMessage(
            ValueError, "Concat must take at least two expressions"
        ):
            Author.objects.annotate(joined=Concat("alias"))

    def test_many(self):
        Author.objects.create(name="Jayden")
        Author.objects.create(name="John Smith", alias="smithj", goes_by="John")
        Author.objects.create(name="Margaret", goes_by="Maggie")
        Author.objects.create(name="Rhonda", alias="adnohR")
        authors = Author.objects.annotate(
            joined=Concat("name", V(" ("), "goes_by", V(")"), output_field=CharField()),
        )
        self.assertQuerySetEqual(
            authors.order_by("name"),
            [
                "Jayden ()",
                "John Smith (John)",
                "Margaret (Maggie)",
                "Rhonda ()",
            ],
            lambda a: a.joined,
        )

    def test_mixed_char_text(self):
        """
        Tests the functionality of the `Concat` function in Django ORM.
        
        This test creates an `Article` instance with a title and a text field containing lorem ipsum. It then uses the `annotate` method to concatenate the title and text fields, separated by a hyphen, and stores the result in a new field `title_text`. The test checks if the concatenated string matches the expected result. The test is performed twice: once with the original concatenated string and once with the concatenated string converted to uppercase.
        """

        Article.objects.create(
            title="The Title", text=lorem_ipsum, written=timezone.now()
        )
        article = Article.objects.annotate(
            title_text=Concat("title", V(" - "), "text", output_field=TextField()),
        ).get(title="The Title")
        self.assertEqual(article.title + " - " + article.text, article.title_text)
        # Wrap the concat in something else to ensure that text is returned
        # rather than bytes.
        article = Article.objects.annotate(
            title_text=Upper(
                Concat("title", V(" - "), "text", output_field=TextField())
            ),
        ).get(title="The Title")
        expected = article.title + " - " + article.text
        self.assertEqual(expected.upper(), article.title_text)

    @skipUnless(connection.vendor == "sqlite", "sqlite specific implementation detail.")
    def test_coalesce_idempotent(self):
        pair = ConcatPair(V("a"), V("b"))
        # Check nodes counts
        self.assertEqual(len(list(pair.flatten())), 3)
        self.assertEqual(
            len(list(pair.coalesce().flatten())), 7
        )  # + 2 Coalesce + 2 Value()
        self.assertEqual(len(list(pair.flatten())), 3)

    def test_sql_generation_idempotency(self):
        qs = Article.objects.annotate(description=Concat("title", V(": "), "summary"))
        # Multiple compilations should not alter the generated query.
        self.assertEqual(str(qs.query), str(qs.all().query))
