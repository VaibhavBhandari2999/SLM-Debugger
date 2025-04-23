from django.db.models import Value
from django.db.models.functions import StrIndex
from django.test import TestCase
from django.utils import timezone

from ..models import Article, Author


class StrIndexTests(TestCase):
    def test_annotate_charfield(self):
        """
        Function: test_annotate_charfield
        Summary: This function tests the annotation of a CharField in a Django model using the StrIndex function. It creates instances of the Author model and then uses the annotate method to add a new field 'fullstop' which is the position of the substring 'R.' in the 'name' field. The function then orders the queryset by the 'name' field and checks if the 'fullstop' field values match the expected results.
        
        Parameters:
        - None
        """

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
        Tests the functionality of the StrIndex function with Unicode values.
        
        This function creates three authors with names containing Unicode characters and then uses the StrIndex function to find the index of the character 'リ' in each name. The results are then ordered by the author names and compared to the expected output.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - None
        """

        Author.objects.create(name='ツリー')
        Author.objects.create(name='皇帝')
        Author.objects.create(name='皇帝 ツリー')
        authors = Author.objects.annotate(sb=StrIndex('name', Value('リ')))
        self.assertQuerysetEqual(authors.order_by('name'), [2, 0, 5], lambda a: a.sb)

    def test_filtering(self):
        """
        Tests filtering of annotated querysets.
        
        This function creates two author entries in the database and then filters the queryset based on the annotated 'middle_name' field. The 'middle_name' field is created by extracting the index of 'R.' from the 'name' field. The function asserts that the filtered queryset contains only the author 'George. R. R. Martin'.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - The function asserts that the filtered
        """

        Author.objects.create(name='George. R. R. Martin')
        Author.objects.create(name='Terry Pratchett')
        self.assertQuerysetEqual(
            Author.objects.annotate(middle_name=StrIndex('name', Value('R.'))).filter(middle_name__gt=0),
            ['George. R. R. Martin'],
            lambda a: a.name
        )
