from django.db.models import TextField
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
        Tests the basic functionality of the Author model with the Coalesce function.
        
        This test creates two instances of the Author model: one with an alias and one without. It then uses the Coalesce function to create a display_name field that prioritizes the alias over the name. The test orders the resulting queryset by name and asserts that the display names are correctly ordered as 'smithj' and 'Rhonda'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Concepts:
        - Author model
        """

        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda')
        authors = Author.objects.annotate(display_name=Coalesce('alias', 'name'))
        self.assertQuerysetEqual(
            authors.order_by('name'), ['smithj', 'Rhonda'],
            lambda a: a.display_name
        )

    def test_gt_two_expressions(self):
        with self.assertRaisesMessage(ValueError, 'Coalesce must take at least two expressions'):
            Author.objects.annotate(display_name=Coalesce('alias'))

    def test_mixed_values(self):
        a1 = Author.objects.create(name='John Smith', alias='smithj')
        a2 = Author.objects.create(name='Rhonda')
        ar1 = Article.objects.create(
            title='How to Django',
            text=lorem_ipsum,
            written=timezone.now(),
        )
        ar1.authors.add(a1)
        ar1.authors.add(a2)
        # mixed Text and Char
        article = Article.objects.annotate(
            headline=Coalesce('summary', 'text', output_field=TextField()),
        )
        self.assertQuerysetEqual(
            article.order_by('title'), [lorem_ipsum],
            lambda a: a.headline
        )
        # mixed Text and Char wrapped
        article = Article.objects.annotate(
            headline=Coalesce(Lower('summary'), Lower('text'), output_field=TextField()),
        )
        self.assertQuerysetEqual(
            article.order_by('title'), [lorem_ipsum.lower()],
            lambda a: a.headline
        )

    def test_ordering(self):
        """
        Tests the ordering of authors based on their alias or name.
        
        This function creates two author objects with different names and aliases. It then tests the ordering of these authors using the `Coalesce` function to prioritize the alias over the name. The function checks the ordering in both ascending and descending order.
        
        Key Parameters:
        - None (the test relies on internal Django objects and methods)
        
        Keywords:
        - Coalesce: A function that returns the first non-null expression among its arguments.
        - order_by: A method
        """

        Author.objects.create(name='John Smith', alias='smithj')
        Author.objects.create(name='Rhonda')
        authors = Author.objects.order_by(Coalesce('alias', 'name'))
        self.assertQuerysetEqual(
            authors, ['Rhonda', 'John Smith'],
            lambda a: a.name
        )
        authors = Author.objects.order_by(Coalesce('alias', 'name').asc())
        self.assertQuerysetEqual(
            authors, ['Rhonda', 'John Smith'],
            lambda a: a.name
        )
        authors = Author.objects.order_by(Coalesce('alias', 'name').desc())
        self.assertQuerysetEqual(
            authors, ['John Smith', 'Rhonda'],
            lambda a: a.name
        )
