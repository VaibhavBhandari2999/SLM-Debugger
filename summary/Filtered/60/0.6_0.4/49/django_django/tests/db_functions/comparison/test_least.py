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
        Test the basic functionality of the Article model with the Least function.
        
        This test creates an Article object with a 'written' timestamp 1 hour before the current time and a 'published' timestamp equal to the current time. It then uses the Least function to find the earliest of the 'written' and 'published' timestamps for the article. The test asserts that the first_updated timestamp, which is the earliest of the two, matches the 'written' timestamp.
        
        Key Parameters:
        - None
        
        Keywords:
        """

        now = timezone.now()
        before = now - timedelta(hours=1)
        Article.objects.create(title='Testing with Django', written=before, published=now)
        articles = Article.objects.annotate(first_updated=Least('written', 'published'))
        self.assertEqual(articles.first().first_updated, before)

    @skipUnlessDBFeature('greatest_least_ignores_nulls')
    def test_ignores_null(self):
        """
        Test to ensure that the function correctly ignores null values when determining the earliest of two dates.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Behavior:
        - Creates an article with a non-null 'written' date.
        - Annotates the article queryset with 'first_updated', which is the earliest of 'written' or 'published' dates.
        - Verifies that the 'first_updated' date for the first article in the queryset is equal to the 'written' date, as the '
        """

        now = timezone.now()
        Article.objects.create(title='Testing with Django', written=now)
        articles = Article.objects.annotate(
            first_updated=Least('written', 'published'),
        )
        self.assertEqual(articles.first().first_updated, now)

    @skipIfDBFeature('greatest_least_ignores_nulls')
    def test_propagates_null(self):
        """
        Tests the behavior of the `Least` function when it encounters a `None` value in the annotated field.
        
        This function creates an `Article` object with a `written` date and then uses the `annotate` method to apply the `Least` function to the `written` and `published` fields. The `published` field is not set, resulting in `None`. The test checks if the `first_updated` field, which is the result of the `Least` function, is `
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
        Tests the workaround for the MySQL Coalesce function in Django ORM.
        
        This function creates a new Article object and then uses RawSQL to create a future datetime object. It then queries the Article model, annotating each article with the last_updated timestamp, which is determined by the minimum of the 'written' or 'published' fields, or the future datetime if either field is null. The test asserts that the first article's last_updated timestamp is the current datetime.
        
        Key Parameters:
        - None
        
        Key Keywords
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
        Tests the functionality of the `test_related_field` method.
        
        This method checks the correct annotation of the lowest age between the author's age and the ages of their fans. It creates an author and a fan, then uses the `annotate` method to find the minimum age between the author and their fans. The expected result is that the lowest age is correctly set to the author's age.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Concepts:
        - Author: A model representing an author
        """

        author = Author.objects.create(name='John Smith', age=45)
        Fan.objects.create(name='Margaret', age=50, author=author)
        authors = Author.objects.annotate(lowest_age=Least('age', 'fans__age'))
        self.assertEqual(authors.first().lowest_age, 45)

    def test_update(self):
        """
        Test the update method for the Author model.
        
        This test case checks the functionality of the update method by updating the 'alias' field of an Author instance using the Least function. The 'alias' field is set to the minimum value between 'name' and 'goes_by'. The test ensures that the 'alias' field is correctly updated to 'James Smith'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Create an Author instance with the name 'James Smith' and
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
