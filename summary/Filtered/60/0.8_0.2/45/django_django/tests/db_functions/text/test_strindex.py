from django.db.models import Value
from django.db.models.functions import StrIndex
from django.test import TestCase
from django.utils import timezone

from ..models import Article, Author


class StrIndexTests(TestCase):
    def test_annotate_charfield(self):
        Author.objects.create(name='George. R. R. Martin')
        Author.objects.create(name='J. R. R. Tolkien')
        Author.objects.create(name='Terry Pratchett')
        authors = Author.objects.annotate(fullstop=StrIndex('name', Value('R.')))
        self.assertQuerysetEqual(authors.order_by('name'), [9, 4, 0], lambda a: a.fullstop)

    def test_annotate_textfield(self):
        Article.objects.create(
            title='How to Django',
            text='This is about How to Django.',
            written=timezone.now(),
        )
        Article.objects.create(
            title='How to Tango',
            text="Won't find anything here.",
            written=timezone.now(),
        )
        articles = Article.objects.annotate(title_pos=StrIndex('text', 'title'))
        self.assertQuerysetEqual(articles.order_by('title'), [15, 0], lambda a: a.title_pos)

    def test_order_by(self):
        Author.objects.create(name='Terry Pratchett')
        Author.objects.create(name='J. R. R. Tolkien')
        Author.objects.create(name='George. R. R. Martin')
        self.assertQuerysetEqual(
            Author.objects.order_by(StrIndex('name', Value('R.')).asc()), [
                'Terry Pratchett',
                'J. R. R. Tolkien',
                'George. R. R. Martin',
            ],
            lambda a: a.name
        )
        self.assertQuerysetEqual(
            Author.objects.order_by(StrIndex('name', Value('R.')).desc()), [
                'George. R. R. Martin',
                'J. R. R. Tolkien',
                'Terry Pratchett',
            ],
            lambda a: a.name
        )

    def test_unicode_values(self):
        """
        Tests the functionality of the StrIndex function with Unicode values in the 'name' field of the Author model.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Steps:
        1. Creates three Author objects with different Unicode names.
        2. Annotates the queryset with the StrIndex function to find the position of the substring 'リ' in the 'name' field.
        3. Orders the queryset by the 'name' field.
        4. Asserts that the annotated values match the expected
        """

        Author.objects.create(name='ツリー')
        Author.objects.create(name='皇帝')
        Author.objects.create(name='皇帝 ツリー')
        authors = Author.objects.annotate(sb=StrIndex('name', Value('リ')))
        self.assertQuerysetEqual(authors.order_by('name'), [2, 0, 5], lambda a: a.sb)

    def test_filtering(self):
        Author.objects.create(name='George. R. R. Martin')
        Author.objects.create(name='Terry Pratchett')
        self.assertQuerysetEqual(
            Author.objects.annotate(middle_name=StrIndex('name', Value('R.'))).filter(middle_name__gt=0),
            ['George. R. R. Martin'],
            lambda a: a.name
        )
