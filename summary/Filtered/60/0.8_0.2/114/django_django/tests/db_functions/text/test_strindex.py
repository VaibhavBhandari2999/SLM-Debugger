from django.db.models import Value
from django.db.models.functions import StrIndex
from django.test import TestCase
from django.utils import timezone

from ..models import Article, Author


class StrIndexTests(TestCase):
    def test_annotate_charfield(self):
        Author.objects.create(name="George. R. R. Martin")
        Author.objects.create(name="J. R. R. Tolkien")
        Author.objects.create(name="Terry Pratchett")
        authors = Author.objects.annotate(fullstop=StrIndex("name", Value("R.")))
        self.assertQuerySetEqual(
            authors.order_by("name"), [9, 4, 0], lambda a: a.fullstop
        )

    def test_annotate_textfield(self):
        """
        Annotate a queryset of Article objects with the position of the 'title' within the 'text' field.
        
        Parameters:
        - None (The function uses a predefined model 'Article' and creates instances of it for testing purposes.)
        
        Returns:
        - A QuerySet of Article objects with an additional annotated field 'title_pos' which is the position of the 'title' within the 'text' field.
        
        Steps:
        1. Create two instances of the Article model with predefined 'title' and 'text
        """

        Article.objects.create(
            title="How to Django",
            text="This is about How to Django.",
            written=timezone.now(),
        )
        Article.objects.create(
            title="How to Tango",
            text="Won't find anything here.",
            written=timezone.now(),
        )
        articles = Article.objects.annotate(title_pos=StrIndex("text", "title"))
        self.assertQuerySetEqual(
            articles.order_by("title"), [15, 0], lambda a: a.title_pos
        )

    def test_order_by(self):
        Author.objects.create(name="Terry Pratchett")
        Author.objects.create(name="J. R. R. Tolkien")
        Author.objects.create(name="George. R. R. Martin")
        self.assertQuerySetEqual(
            Author.objects.order_by(StrIndex("name", Value("R.")).asc()),
            [
                "Terry Pratchett",
                "J. R. R. Tolkien",
                "George. R. R. Martin",
            ],
            lambda a: a.name,
        )
        self.assertQuerySetEqual(
            Author.objects.order_by(StrIndex("name", Value("R.")).desc()),
            [
                "George. R. R. Martin",
                "J. R. R. Tolkien",
                "Terry Pratchett",
            ],
            lambda a: a.name,
        )

    def test_unicode_values(self):
        """
        Tests the functionality of the StrIndex function with Unicode values in a database query.
        
        This function creates three author entries with different names containing Unicode characters. It then uses the StrIndex function to find the position of the character 'リ' in each name. The results are ordered by the author names and compared to expected values.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Methods:
        - `test_unicode_values`: Creates and queries author objects to test StrIndex with Unicode.
        
        Important Notes:
        """

        Author.objects.create(name="ツリー")
        Author.objects.create(name="皇帝")
        Author.objects.create(name="皇帝 ツリー")
        authors = Author.objects.annotate(sb=StrIndex("name", Value("リ")))
        self.assertQuerySetEqual(authors.order_by("name"), [2, 0, 5], lambda a: a.sb)

    def test_filtering(self):
        Author.objects.create(name="George. R. R. Martin")
        Author.objects.create(name="Terry Pratchett")
        self.assertQuerySetEqual(
            Author.objects.annotate(middle_name=StrIndex("name", Value("R."))).filter(
                middle_name__gt=0
            ),
            ["George. R. R. Martin"],
            lambda a: a.name,
        )
