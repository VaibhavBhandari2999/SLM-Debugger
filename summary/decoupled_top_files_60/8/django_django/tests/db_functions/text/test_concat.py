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
        """
        Function: test_many
        Summary: This function tests the creation and annotation of authors in a database. It creates multiple author entries with different names and aliases, and then annotates each entry with a custom joined field that combines the name and goes_by fields. The function asserts that the resulting queryset is ordered by the name field and matches the expected output.
        
        Parameters:
        - None
        
        Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - A queryset of Author objects with an annotated 'joined'
        """

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
        Test the idempotence of the coalesce method on a ConcatPair object.
        
        This test ensures that applying the coalesce method to a ConcatPair object multiple times does not change the object's state.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Create a ConcatPair object with two variables 'a' and 'b'.
        2. Check the number of nodes in the flattened representation of the ConcatPair object.
        3. Apply the coalesce method to the ConcatPair object and
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
