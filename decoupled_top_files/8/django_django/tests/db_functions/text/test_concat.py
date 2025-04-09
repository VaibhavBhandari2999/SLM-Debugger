"""
```python
"""
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
        Tests the basic functionality of the `Author` model's annotation with `Concat`.
        
        Creates four `Author` objects with different names, aliases, and goes_by fields.
        Annotates the queryset with the concatenated values of `alias` and `goes_by`.
        Orders the queryset by name and asserts that the concatenated values match the expected output.
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
        """
        Tests the functionality of creating and annotating author objects with concatenated names and aliases. Creates four author instances with different names, aliases, and goes_by fields. Annotates these instances by concatenating the name and goes_by fields with specific delimiters. Orders the annotated queryset by name and asserts that the concatenated values match the expected output.
        
        Important Functions:
        - `Author.objects.create()`: Creates new author instances.
        - `annotate()`: Adds a new field to each object in the queryset
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
        """
        Tests the concatenation of title and text fields in an Article model using Django's F expressions. The function creates an Article instance with a given title and text, then annotates the queryset with a concatenated field. It asserts that the concatenated field matches the expected result both in its original form and after being converted to uppercase.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `Article.objects.create()`: Creates a new Article instance.
        - `annotate()`:
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
        Tests the idempotence of the coalesce method on a ConcatPair.
        
        This function checks that applying the coalesce method multiple times to a ConcatPair does not change its flattened node count. The ConcatPair is created with two values 'a' and 'b'. Initially, the flattened node count is 3. After applying coalesce, the flattened node count increases by 2 (for the Coalesce and Value nodes). Applying coalesce again does not alter the node count, confirming its id
        """

        pair = ConcatPair(V('a'), V('b'))
        # Check nodes counts
        self.assertEqual(len(list(pair.flatten())), 3)
        self.assertEqual(len(list(pair.coalesce().flatten())), 7)  # + 2 Coalesce + 2 Value()
        self.assertEqual(len(list(pair.flatten())), 3)

    def test_sql_generation_idempotency(self):
        """
        Tests the idempotency of SQL generation for an annotated queryset.
        
        This function checks if multiple compilations of the same annotated queryset
        produce the same SQL query. It uses the `Concat` function to concatenate
        'title' and 'summary' fields with a colon and space in between, and then
        compares the generated query string of the annotated queryset with that of
        its compiled version.
        
        Args:
        None
        
        Returns:
        None
        """

        qs = Article.objects.annotate(description=Concat('title', V(': '), 'summary'))
        # Multiple compilations should not alter the generated query.
        self.assertEqual(str(qs.query), str(qs.all().query))
