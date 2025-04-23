from django.db.models import Value
from django.db.models.functions import StrIndex
from django.test import TestCase
from django.utils import timezone

from ..models import Article, Author


class StrIndexTests(TestCase):
    def test_annotate_charfield(self):
        """
        Test the annotate method on a CharField.
        
        This function creates three authors with different names and then uses the annotate method to add a new field `fullstop` to each author object. The `fullstop` field is calculated using the StrIndex function to find the position of 'R.' in the author's name. The function then orders the authors by their names and checks if the positions of 'R.' in their names are correctly annotated.
        
        Parameters:
        - None
        
        Returns:
        - None
        """

        Author.objects.create(name='George. R. R. Martin')
        Author.objects.create(name='J. R. R. Tolkien')
        Author.objects.create(name='Terry Pratchett')
        authors = Author.objects.annotate(fullstop=StrIndex('name', Value('R.')))
        self.assertQuerysetEqual(authors.order_by('name'), [9, 4, 0], lambda a: a.fullstop)

    def test_annotate_textfield(self):
        """
        Annotate and query articles based on the position of the title within the text.
        
        This function creates two articles with specific titles and texts, then annotates each article with the position of its title within the text. The annotated positions are then ordered by the article's title and compared to expected values.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Create two articles with predefined titles and texts.
        2. Annotate each article with the position of its title within the
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
        Author.objects.create(name='ツリー')
        Author.objects.create(name='皇帝')
        Author.objects.create(name='皇帝 ツリー')
        authors = Author.objects.annotate(sb=StrIndex('name', Value('リ')))
        self.assertQuerysetEqual(authors.order_by('name'), [2, 0, 5], lambda a: a.sb)

    def test_filtering(self):
        """
        Test filtering authors based on the position of a specific substring in their names.
        
        This function creates two author entries in the database and then filters the authors based on the position of the substring 'R.' in their names. The function asserts that the filtered queryset contains the expected author.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Elements:
        - `Author.objects.create(name='George. R. R. Martin')`: Creates an author with the name 'George. R. R. Martin'.
        """

        Author.objects.create(name='George. R. R. Martin')
        Author.objects.create(name='Terry Pratchett')
        self.assertQuerysetEqual(
            Author.objects.annotate(middle_name=StrIndex('name', Value('R.'))).filter(middle_name__gt=0),
            ['George. R. R. Martin'],
            lambda a: a.name
        )
