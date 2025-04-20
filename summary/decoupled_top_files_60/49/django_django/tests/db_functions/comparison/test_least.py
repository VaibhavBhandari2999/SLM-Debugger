from datetime import datetime, timedelta
from decimal import Decimal
from unittest import skipIf, skipUnless

from django.db import connection
from django.db.models.expressions import RawSQL
from django.db.models.functions import Coalesce, Least
from django.test import TestCase, skipIfDBFeature, skipUnlessDBFeature
from django.utils import timezone

from ..models import Article, Author, DecimalModel, Fan


class LeastTests(TestCase):

    def test_basic(self):
        """
        Test the basic functionality of the Article model's annotation with the Least function.
        
        This test creates an Article instance with a specific 'written' and 'published' timestamp. It then uses the annotate method to add a new field 'first_updated' to the queryset, which is the minimum of 'written' and 'published' timestamps. The test asserts that the 'first_updated' field for the first article in the queryset is equal to the 'written' timestamp, which is set to be 1
        """

        now = timezone.now()
        before = now - timedelta(hours=1)
        Article.objects.create(title='Testing with Django', written=before, published=now)
        articles = Article.objects.annotate(first_updated=Least('written', 'published'))
        self.assertEqual(articles.first().first_updated, before)

    @skipUnlessDBFeature('greatest_least_ignores_nulls')
    def test_ignores_null(self):
        now = timezone.now()
        Article.objects.create(title='Testing with Django', written=now)
        articles = Article.objects.annotate(
            first_updated=Least('written', 'published'),
        )
        self.assertEqual(articles.first().first_updated, now)

    @skipIfDBFeature('greatest_least_ignores_nulls')
    def test_propagates_null(self):
        """
        Tests the behavior of the `Least` function when applied to fields that may contain null values.
        
        This function creates a new `Article` instance and then uses the `annotate` method with the `Least` function to find the earliest of the 'written' and 'published' dates. It asserts that the `first_updated` field, which is the result of the `Least` function, is `None`.
        
        Key Parameters:
        - None
        
        Returns:
        - None
        """

        Article.objects.create(title='Testing with Django', written=timezone.now())
        articles = Article.objects.annotate(first_updated=Least('written', 'published'))
        self.assertIsNone(articles.first().first_updated)

    @skipIf(connection.vendor == 'mysql', "This doesn't work on MySQL")
    def test_coalesce_workaround(self):
        future = datetime(2100, 1, 1)
        now = timezone.now()
        Article.objects.create(title='Testing with Django', written=now)
        articles = Article.objects.annotate(
            last_updated=Least(
                Coalesce('written', future),
                Coalesce('published', future),
            ),
        )
        self.assertEqual(articles.first().last_updated, now)

    @skipUnless(connection.vendor == 'mysql', "MySQL-specific workaround")
    def test_coalesce_workaround_mysql(self):
        future = datetime(2100, 1, 1)
        now = timezone.now()
        Article.objects.create(title='Testing with Django', written=now)
        future_sql = RawSQL("cast(%s as datetime)", (future,))
        articles = Article.objects.annotate(
            last_updated=Least(
                Coalesce('written', future_sql),
                Coalesce('published', future_sql),
            ),
        )
        self.assertEqual(articles.first().last_updated, now)

    def test_all_null(self):
        """
        Test the behavior of the 'first_updated' field when all fields (published and updated) are null.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Behavior:
        - Creates a new Article instance with a non-null 'title' and a non-null 'written' timestamp.
        - Annotates the queryset with 'first_updated', which is the minimum value between 'published' and 'updated'.
        - Asserts that the 'first_updated' field of the first article in the queryset is None
        """

        Article.objects.create(title='Testing with Django', written=timezone.now())
        articles = Article.objects.annotate(first_updated=Least('published', 'updated'))
        self.assertIsNone(articles.first().first_updated)

    def test_one_expressions(self):
        with self.assertRaisesMessage(ValueError, 'Least must take at least two expressions'):
            Least('written')

    def test_related_field(self):
        author = Author.objects.create(name='John Smith', age=45)
        Fan.objects.create(name='Margaret', age=50, author=author)
        authors = Author.objects.annotate(lowest_age=Least('age', 'fans__age'))
        self.assertEqual(authors.first().lowest_age, 45)

    def test_update(self):
        author = Author.objects.create(name='James Smith', goes_by='Jim')
        Author.objects.update(alias=Least('name', 'goes_by'))
        author.refresh_from_db()
        self.assertEqual(author.alias, 'James Smith')

    def test_decimal_filter(self):
        """
        Tests the 'Least' function with Decimal fields.
        
        This function creates a DecimalModel instance with two Decimal fields, n1 and n2, and then filters the model instances based on the 'Least' function applied to these fields. The 'Least' function returns the smaller of the two Decimal values. The test checks if the filter correctly identifies the instance where the least value is 1.1.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key elements:
        - DecimalModel: A model with
        """

        obj = DecimalModel.objects.create(n1=Decimal('1.1'), n2=Decimal('1.2'))
        self.assertCountEqual(
            DecimalModel.objects.annotate(
                least=Least('n1', 'n2'),
            ).filter(least=Decimal('1.1')),
            [obj],
        )
