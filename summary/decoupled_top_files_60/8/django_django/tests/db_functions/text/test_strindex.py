from django.db.models import Value
from django.db.models.functions import StrIndex
from django.test import TestCase
from django.utils import timezone

from ..models import Article, Author


class StrIndexTests(TestCase):
    def test_annotate_charfield(self):
        """
        Annotate a queryset of Author objects with the index of the substring 'R.' in the 'name' field.
        
        Parameters:
        - None
        
        Returns:
        - A queryset of Author objects with an additional annotated field 'fullstop' which is the index of the substring 'R.' in the 'name' field.
        
        Steps:
        1. Create three Author objects with different names.
        2. Annotate the queryset of Author objects with the index of the substring 'R.' in the 'name'
        """

        Author.objects.create(name='George. R. R. Martin')
        Author.objects.create(name='J. R. R. Tolkien')
        Author.objects.create(name='Terry Pratchett')
        authors = Author.objects.annotate(fullstop=StrIndex('name', Value('R.')))
        self.assertQuerysetEqual(authors.order_by('name'), [9, 4, 0], lambda a: a.fullstop)

    def test_annotate_textfield(self):
        """
        Function: test_annotate_textfield
        
        This function tests the annotation of a text field in a Django model using the StrIndex function.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Steps:
        1. Creates two instances of the Article model with specified title and text fields.
        2. Annotates the queryset of articles with a new field `title_pos` which is the position of the title in the text field.
        3. Orders the annotated queryset by the title field.
        4. Assert
        """

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
        
        This test creates three Author objects with different names containing Unicode characters. It then uses the StrIndex function to find the position of the character 'リ' in each name and orders the results. The test asserts that the positions are as expected.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Points:
        - Creates three Author objects with names 'ツリー', '皇帝', and '皇帝
        """

        Author.objects.create(name='ツリー')
        Author.objects.create(name='皇帝')
        Author.objects.create(name='皇帝 ツリー')
        authors = Author.objects.annotate(sb=StrIndex('name', Value('リ')))
        self.assertQuerysetEqual(authors.order_by('name'), [2, 0, 5], lambda a: a.sb)

    def test_filtering(self):
        """
        Tests filtering of annotated queryset.
        
        This function creates two authors in the database and then filters the queryset based on the annotated 'middle_name' field. The 'middle_name' field is created by using the StrIndex function to find the index of 'R.' in the 'name' field. The function then filters the queryset to include only those authors where the index of 'R.' is greater than 0. The expected result is that only 'George. R. R. Martin' is included in
        """

        Author.objects.create(name='George. R. R. Martin')
        Author.objects.create(name='Terry Pratchett')
        self.assertQuerysetEqual(
            Author.objects.annotate(middle_name=StrIndex('name', Value('R.'))).filter(middle_name__gt=0),
            ['George. R. R. Martin'],
            lambda a: a.name
        )
