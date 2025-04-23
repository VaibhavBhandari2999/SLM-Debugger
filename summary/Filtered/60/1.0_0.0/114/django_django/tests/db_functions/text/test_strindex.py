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
        """
        Tests the ordering of authors based on a substring of their names.
        
        This function creates three author objects with different names and then tests the ordering of these objects based on a specific substring of their names. The substring is "R." and the ordering can be either ascending or descending.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - The first query should return the authors in the order: Terry Pratchett, J. R. R. Tolkien, George. R. R. Martin.
        """

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
        Author.objects.create(name="ツリー")
        Author.objects.create(name="皇帝")
        Author.objects.create(name="皇帝 ツリー")
        authors = Author.objects.annotate(sb=StrIndex("name", Value("リ")))
        self.assertQuerySetEqual(authors.order_by("name"), [2, 0, 5], lambda a: a.sb)

    def test_filtering(self):
        """
        Tests filtering of authors based on the presence of a specific substring in their names.
        
        This function creates two author entries in the database and then filters the authors based on the presence of the substring "R." in their names. The test checks if the filtered queryset contains the expected author.
        
        Key Parameters:
        - None
        
        Input:
        - None
        
        Output:
        - None
        
        Assertions:
        - The filtered queryset should contain the author "George. R. R. Martin".
        - The author "Terry Pratchett
        """

        Author.objects.create(name="George. R. R. Martin")
        Author.objects.create(name="Terry Pratchett")
        self.assertQuerySetEqual(
            Author.objects.annotate(middle_name=StrIndex("name", Value("R."))).filter(
                middle_name__gt=0
            ),
            ["George. R. R. Martin"],
            lambda a: a.name,
        )
