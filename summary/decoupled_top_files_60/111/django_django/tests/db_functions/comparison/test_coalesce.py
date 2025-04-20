from django.db.models import Subquery, TextField
from django.db.models.functions import Coalesce, Lower
from django.test import TestCase
from django.utils import timezone

from ..models import Article, Author

lorem_ipsum = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua."""


class CoalesceTests(TestCase):
    def test_basic(self):
        """
        Tests the basic functionality of the Author model's annotation with Coalesce function.
        
        This test creates two Author objects with different attributes and then uses the annotate method to add a new field `display_name` to each object. The `display_name` field is created using the Coalesce function, which returns the value of "alias" if it is not null, otherwise it returns the value of "name". The test then orders the resulting queryset by the "name" field and checks if the `display
        """

        Author.objects.create(name="John Smith", alias="smithj")
        Author.objects.create(name="Rhonda")
        authors = Author.objects.annotate(display_name=Coalesce("alias", "name"))
        self.assertQuerySetEqual(
            authors.order_by("name"), ["smithj", "Rhonda"], lambda a: a.display_name
        )

    def test_gt_two_expressions(self):
        with self.assertRaisesMessage(
            ValueError, "Coalesce must take at least two expressions"
        ):
            Author.objects.annotate(display_name=Coalesce("alias"))

    def test_mixed_values(self):
        """
        Tests the functionality of the Coalesce function in Django ORM when used with mixed Text and Char fields.
        
        This test function creates a couple of authors and an article. It then uses the Coalesce function to handle mixed Text and Char fields, ensuring that if the summary field is null, the text field is used as a fallback. The test checks that the correct headline is generated based on the presence of a summary or text field.
        
        Key Parameters:
        - None
        
        Keywords:
        - Coalesce
        - Text
        """

        a1 = Author.objects.create(name="John Smith", alias="smithj")
        a2 = Author.objects.create(name="Rhonda")
        ar1 = Article.objects.create(
            title="How to Django",
            text=lorem_ipsum,
            written=timezone.now(),
        )
        ar1.authors.add(a1)
        ar1.authors.add(a2)
        # mixed Text and Char
        article = Article.objects.annotate(
            headline=Coalesce("summary", "text", output_field=TextField()),
        )
        self.assertQuerySetEqual(
            article.order_by("title"), [lorem_ipsum], lambda a: a.headline
        )
        # mixed Text and Char wrapped
        article = Article.objects.annotate(
            headline=Coalesce(
                Lower("summary"), Lower("text"), output_field=TextField()
            ),
        )
        self.assertQuerySetEqual(
            article.order_by("title"), [lorem_ipsum.lower()], lambda a: a.headline
        )

    def test_ordering(self):
        Author.objects.create(name="John Smith", alias="smithj")
        Author.objects.create(name="Rhonda")
        authors = Author.objects.order_by(Coalesce("alias", "name"))
        self.assertQuerySetEqual(authors, ["Rhonda", "John Smith"], lambda a: a.name)
        authors = Author.objects.order_by(Coalesce("alias", "name").asc())
        self.assertQuerySetEqual(authors, ["Rhonda", "John Smith"], lambda a: a.name)
        authors = Author.objects.order_by(Coalesce("alias", "name").desc())
        self.assertQuerySetEqual(authors, ["John Smith", "Rhonda"], lambda a: a.name)

    def test_empty_queryset(self):
        Author.objects.create(name="John Smith")
        queryset = Author.objects.values("id")
        tests = [
            (queryset.none(), "QuerySet.none()"),
            (queryset.filter(id=0), "QuerySet.filter(id=0)"),
            (Subquery(queryset.none()), "Subquery(QuerySet.none())"),
            (Subquery(queryset.filter(id=0)), "Subquery(Queryset.filter(id=0)"),
        ]
        for empty_query, description in tests:
            with self.subTest(description), self.assertNumQueries(1):
                qs = Author.objects.annotate(annotation=Coalesce(empty_query, 42))
                self.assertEqual(qs.first().annotation, 42)
qual(qs.first().annotation, 42)
