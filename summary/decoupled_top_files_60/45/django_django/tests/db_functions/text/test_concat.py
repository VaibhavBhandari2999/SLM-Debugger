from unittest import skipUnless

from django.db import connection
from django.db.models import CharField, TextField, Value as V
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
        Test the basic functionality of the Author model's annotation with Concat.
        
        This test creates four Author objects with different names, aliases, and goes_by fields. It then annotates the queryset with a Concat of 'alias' and 'goes_by' fields and orders the results by 'name'. The test checks if the concatenated values are as expected.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - The order of the concatenated values should match the expected output: ['', 'smithjJohn
        """

        Author.objects.create(name='Jayden')
        Author.objects.create(name='John Smith', alias='smithj', goes_by='John')
        Author.objects.create(name='Margaret', goes_by='Maggie')
        Author.objects.create(name='Rhonda', alias='adnohR')
        authors = Author.objects.annotate(joined=Concat('alias', 'goes_by'))
        self.assertQuerysetEqual(
            authors.order_by('name'), [
                '',
                'smithjJohn',
                'Maggie',
                'adnohR',
            ],
            lambda a: a.joined
        )

    def test_gt_two_expressions(self):
        with self.assertRaisesMessage(ValueError, 'Concat must take at least two expressions'):
            Author.objects.annotate(joined=Concat('alias'))

    def test_many(self):
        Author.objects.create(name='Jayden')
        Author.objects.create(name='John Smith', alias='smithj', goes_by='John')
        Author.objects.create(name='Margaret', goes_by='Maggie')
        Author.objects.create(name='Rhonda', alias='adnohR')
        authors = Author.objects.annotate(
            joined=Concat('name', V(' ('), 'goes_by', V(')'), output_field=CharField()),
        )
        self.assertQuerysetEqual(
            authors.order_by('name'), [
                'Jayden ()',
                'John Smith (John)',
                'Margaret (Maggie)',
                'Rhonda ()',
            ],
            lambda a: a.joined
        )

    def test_mixed_char_text(self):
        """
        Test the concatenation and transformation of 'title' and 'text' fields in the Article model.
        
        This test function creates an instance of the Article model with a specified 'title' and 'text'. It then annotates the query to concatenate the 'title' and 'text' fields, separated by a hyphen, and ensures that the concatenated result matches the expected value. The test is performed twice: once with a simple concatenation and once with the result converted to uppercase.
        
        Key Parameters:
        -
        """

        Article.objects.create(title='The Title', text=lorem_ipsum, written=timezone.now())
        article = Article.objects.annotate(
            title_text=Concat('title', V(' - '), 'text', output_field=TextField()),
        ).get(title='The Title')
        self.assertEqual(article.title + ' - ' + article.text, article.title_text)
        # Wrap the concat in something else to ensure that text is returned
        # rather than bytes.
        article = Article.objects.annotate(
            title_text=Upper(Concat('title', V(' - '), 'text', output_field=TextField())),
        ).get(title='The Title')
        expected = article.title + ' - ' + article.text
        self.assertEqual(expected.upper(), article.title_text)

    @skipUnless(connection.vendor == 'sqlite', "sqlite specific implementation detail.")
    def test_coalesce_idempotent(self):
        """
        Tests the idempotence of the coalesce method on a ConcatPair object.
        
        This method checks the number of nodes in a ConcatPair object before and after applying the coalesce method. The coalesce method is expected to modify the structure of the ConcatPair, increasing the number of nodes, but applying it twice should not change the structure further.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - A ConcatPair object is created with two variables 'a' and 'b'.
        """

        pair = ConcatPair(V('a'), V('b'))
        # Check nodes counts
        self.assertEqual(len(list(pair.flatten())), 3)
        self.assertEqual(len(list(pair.coalesce().flatten())), 7)  # + 2 Coalesce + 2 Value()
        self.assertEqual(len(list(pair.flatten())), 3)

    def test_sql_generation_idempotency(self):
        qs = Article.objects.annotate(description=Concat('title', V(': '), 'summary'))
        # Multiple compilations should not alter the generated query.
        self.assertEqual(str(qs.query), str(qs.all().query))
rtEqual(str(qs.query), str(qs.all().query))
