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
        Tests the functionality of the `Least` function in Django's ORM.
        
        This test creates an `Article` object with a `written` timestamp one hour before the current time and a `published` timestamp equal to the current time. It then uses the `annotate` method with the `Least` function to find the earliest of the `written` and `published` timestamps for each article. The test asserts that the first article's `first_updated` timestamp, which is the earliest of the two,
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
        Tests the behavior of the 'first_updated' property, which is annotated using the Least function to determine the earliest of the 'written' or 'published' dates. This test specifically checks if the 'first_updated' property returns None when no 'published' date is provided.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - An 'Article' object is created with a 'written' date but no 'published' date.
        - The 'first_updated' property is annotated as the
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
        """
        Tests the coalesce workaround for MySQL.
        
        This function creates a new article with a specific 'written' date and then queries the database to find the article. It uses RawSQL to handle MySQL-specific datetime casting and annotates the query to find the minimum of either 'written' or 'published' dates, using a workaround for MySQL's Coalesce function. The expected result is that the 'last_updated' field of the first article should match the 'written' date.
        
        Parameters:
        - None
        
        Returns
        """

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
        """
        Tests the functionality of a related field with a Least aggregation.
        
        This function creates an author and a fan, then uses the annotate method to add a new field 'lowest_age' to the Author queryset. This field is calculated as the minimum age between the author's age and the age of their fans. The test checks if the 'lowest_age' for the first author in the queryset is 45, which is the minimum age between the author and the fan.
        
        Parameters:
        - None
        
        Returns:
        """

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
        
        This function creates a DecimalModel instance with two Decimal fields, n1 and n2, and then filters the model instances based on the 'Least' function applied to these fields. The 'Least' function returns the smaller of the two Decimal values. The test checks if the filtered result contains the expected object.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        -
        """

        obj = DecimalModel.objects.create(n1=Decimal('1.1'), n2=Decimal('1.2'))
        self.assertCountEqual(
            DecimalModel.objects.annotate(
                least=Least('n1', 'n2'),
            ).filter(least=Decimal('1.1')),
            [obj],
        )
