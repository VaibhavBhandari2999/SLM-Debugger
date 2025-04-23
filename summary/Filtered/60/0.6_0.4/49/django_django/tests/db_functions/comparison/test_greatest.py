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
        Tests the functionality of the `Greatest` function in Django ORM.
        
        This test creates an `Article` object with a `written` timestamp one hour before the current time and a `published` timestamp equal to the current time. It then annotates the queryset with the `last_updated` field, which is the greatest of the `written` and `published` timestamps. The test asserts that the `last_updated` field for the first article in the queryset is equal to the current time.
        
        Key
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
        Tests the coalesce workaround in Django ORM.
        
        This function creates an 'Article' object with a 'written' datetime field set to the current time. It then queries the database to annotate each article with a 'last_updated' field, which is the maximum of the 'written' or 'published' fields, defaulting to a past date if either field is null. The test asserts that the 'last_updated' field of the first article is set to the current time.
        
        Parameters:
        None
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
        - Creates a new 'Article' object with a non-null 'title' and a non-null 'written' timestamp.
        - Annotates the 'Article' queryset with 'last_updated', which is the greatest value between 'published' and 'updated' fields.
        - Asserts that the 'last
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
        Tests the functionality of the Greatest function with Decimal fields in a database query.
        
        This function creates a DecimalModel instance with two Decimal fields, n1 and n2, each containing a specific Decimal value. It then uses the Greatest function to find the maximum value between n1 and n2 for each instance. The function filters the annotated queryset to find instances where the greatest value is Decimal('1.2') and checks if the result matches the expected object.
        
        Parameters:
        - None
        
        Returns:
        - None
        """

        obj = DecimalModel.objects.create(n1=Decimal('1.1'), n2=Decimal('1.2'))
        self.assertCountEqual(
            DecimalModel.objects.annotate(
                greatest=Greatest('n1', 'n2'),
            ).filter(greatest=Decimal('1.2')),
            [obj],
        )
