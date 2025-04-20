from datetime import datetime, timedelta
from decimal import Decimal
from unittest import skipIf, skipUnless

from django.db import connection
from django.db.models.expressions import RawSQL
from django.db.models.functions import Coalesce, Greatest
from django.test import TestCase, skipIfDBFeature, skipUnlessDBFeature
from django.utils import timezone

from ..models import Article, Author, DecimalModel, Fan


class GreatestTests(TestCase):

    def test_basic(self):
        """
        Test the basic functionality of the Article model with the Greatest function.
        
        This test creates an Article object with a 'written' timestamp from one hour ago and a 'published' timestamp set to the current time. It then uses the Greatest function to annotate the query with the latest of the two timestamps. The test asserts that the annotated 'last_updated' field is set to the current time.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - Creates an Article instance with specific 'written
        """

        now = timezone.now()
        before = now - timedelta(hours=1)
        Article.objects.create(title='Testing with Django', written=before, published=now)
        articles = Article.objects.annotate(last_updated=Greatest('written', 'published'))
        self.assertEqual(articles.first().last_updated, now)

    @skipUnlessDBFeature('greatest_least_ignores_nulls')
    def test_ignores_null(self):
        now = timezone.now()
        Article.objects.create(title='Testing with Django', written=now)
        articles = Article.objects.annotate(last_updated=Greatest('written', 'published'))
        self.assertEqual(articles.first().last_updated, now)

    @skipIfDBFeature('greatest_least_ignores_nulls')
    def test_propagates_null(self):
        Article.objects.create(title='Testing with Django', written=timezone.now())
        articles = Article.objects.annotate(last_updated=Greatest('written', 'published'))
        self.assertIsNone(articles.first().last_updated)

    @skipIf(connection.vendor == 'mysql', "This doesn't work on MySQL")
    def test_coalesce_workaround(self):
        """
        Test the coalesce workaround for handling null values in Django ORM.
        
        This function creates a new Article instance with a specific title and a current timestamp. It then annotates the queryset with a 'last_updated' field, which is determined by the greatest value between the 'written' and 'published' fields. If either of these fields is null, it defaults to a past date (1900-01-01). The function asserts that the 'last_updated' field of the
        """

        past = datetime(1900, 1, 1)
        now = timezone.now()
        Article.objects.create(title='Testing with Django', written=now)
        articles = Article.objects.annotate(
            last_updated=Greatest(
                Coalesce('written', past),
                Coalesce('published', past),
            ),
        )
        self.assertEqual(articles.first().last_updated, now)

    @skipUnless(connection.vendor == 'mysql', "MySQL-specific workaround")
    def test_coalesce_workaround_mysql(self):
        past = datetime(1900, 1, 1)
        now = timezone.now()
        Article.objects.create(title='Testing with Django', written=now)
        past_sql = RawSQL("cast(%s as datetime)", (past,))
        articles = Article.objects.annotate(
            last_updated=Greatest(
                Coalesce('written', past_sql),
                Coalesce('published', past_sql),
            ),
        )
        self.assertEqual(articles.first().last_updated, now)

    def test_all_null(self):
        """
        Method to test the behavior of the 'last_updated' field when all related fields ('published' and 'updated') are null.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - Creates a new 'Article' object with a title and a current timestamp for 'written'.
        - Annotates the 'Article' queryset with 'last_updated', which is the greatest value between 'published' and 'updated'.
        - Asserts that the 'last_updated' field of the first article
        """

        Article.objects.create(title='Testing with Django', written=timezone.now())
        articles = Article.objects.annotate(last_updated=Greatest('published', 'updated'))
        self.assertIsNone(articles.first().last_updated)

    def test_one_expressions(self):
        with self.assertRaisesMessage(ValueError, 'Greatest must take at least two expressions'):
            Greatest('written')

    def test_related_field(self):
        author = Author.objects.create(name='John Smith', age=45)
        Fan.objects.create(name='Margaret', age=50, author=author)
        authors = Author.objects.annotate(highest_age=Greatest('age', 'fans__age'))
        self.assertEqual(authors.first().highest_age, 50)

    def test_update(self):
        author = Author.objects.create(name='James Smith', goes_by='Jim')
        Author.objects.update(alias=Greatest('name', 'goes_by'))
        author.refresh_from_db()
        self.assertEqual(author.alias, 'Jim')

    def test_decimal_filter(self):
        """
        Tests the `Greatest` function with Decimal fields.
        
        This function creates a DecimalModel instance with two Decimal fields, n1 and n2, and then filters the model instances based on the greatest value between n1 and n2. The test checks if the instance with the greatest value (1.2) is correctly filtered.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - None
        
        Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - None
        """

        obj = DecimalModel.objects.create(n1=Decimal('1.1'), n2=Decimal('1.2'))
        self.assertCountEqual(
            DecimalModel.objects.annotate(
                greatest=Greatest('n1', 'n2'),
            ).filter(greatest=Decimal('1.2')),
            [obj],
        )
