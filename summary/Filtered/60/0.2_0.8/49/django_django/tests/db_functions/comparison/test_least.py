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
        now = timezone.now()
        before = now - timedelta(hours=1)
        Article.objects.create(title='Testing with Django', written=before, published=now)
        articles = Article.objects.annotate(first_updated=Least('written', 'published'))
        self.assertEqual(articles.first().first_updated, before)

    @skipUnlessDBFeature('greatest_least_ignores_nulls')
    def test_ignores_null(self):
        """
        Function: test_ignores_null
        
        This function tests the behavior of the 'Least' function in Django's ORM when dealing with null values. It creates an 'Article' object with a 'written' timestamp and then uses the 'annotate' method to find the earliest of 'written' or 'published' dates. The test asserts that when 'published' is null, 'written' is returned as the 'first_updated' date.
        
        Parameters:
        - None
        
        Keywords:
        - 'Least':
        """

        now = timezone.now()
        Article.objects.create(title='Testing with Django', written=now)
        articles = Article.objects.annotate(
            first_updated=Least('written', 'published'),
        )
        self.assertEqual(articles.first().first_updated, now)

    @skipIfDBFeature('greatest_least_ignores_nulls')
    def test_propagates_null(self):
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
        """
        Update the alias field of an Author instance based on the minimum value between the name and goes_by fields.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Create an Author instance with the name 'James Smith' and goes_by 'Jim'.
        2. Update the alias field of the Author instance to be the minimum value between the name and goes_by fields.
        3. Refresh the Author instance from the database.
        4. Assert that the alias field is set to 'James Smith',
        """

        author = Author.objects.create(name='James Smith', goes_by='Jim')
        Author.objects.update(alias=Least('name', 'goes_by'))
        author.refresh_from_db()
        self.assertEqual(author.alias, 'James Smith')

    def test_decimal_filter(self):
        obj = DecimalModel.objects.create(n1=Decimal('1.1'), n2=Decimal('1.2'))
        self.assertCountEqual(
            DecimalModel.objects.annotate(
                least=Least('n1', 'n2'),
            ).filter(least=Decimal('1.1')),
            [obj],
        )
 
