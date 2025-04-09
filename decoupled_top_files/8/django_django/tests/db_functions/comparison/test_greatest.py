"""
The provided Python file contains unit tests for various functionalities involving Django's ORM and SQL functions, specifically focusing on the `Greatest` function. The tests cover different scenarios such as handling null values, working around database limitations, and applying the `Greatest` function to related models and decimal fields. Each test method is annotated with appropriate decorators to skip or run based on database features, ensuring compatibility across different database systems. The file includes detailed docstrings for each test method, explaining the purpose and key steps involved. ```python
"""
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
        Tests the basic functionality of annotating an Article queryset with the latest of its 'written' or 'published' timestamps.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `timezone.now()`: Retrieves the current date and time.
        - `timedelta(hours=1)`: Creates a timedelta object representing 1 hour.
        - `Article.objects.create(...)`: Creates a new Article instance with specified attributes.
        - `Greatest('written', 'published
        """

        now = timezone.now()
        before = now - timedelta(hours=1)
        Article.objects.create(title='Testing with Django', written=before, published=now)
        articles = Article.objects.annotate(last_updated=Greatest('written', 'published'))
        self.assertEqual(articles.first().last_updated, now)

    @skipUnlessDBFeature('greatest_least_ignores_nulls')
    def test_ignores_null(self):
        """
        Tests that the `Greatest` function correctly ignores null values when annotating an object's last updated timestamp.
        
        This function creates an `Article` instance with a non-null `written` date and uses the `annotate` method with `Greatest` to determine the last updated timestamp. The test asserts that the last updated timestamp matches the `written` date, indicating that null values are properly ignored.
        
        Functions Used:
        - `timezone.now()`: Retrieves the current date and time.
        """

        now = timezone.now()
        Article.objects.create(title='Testing with Django', written=now)
        articles = Article.objects.annotate(last_updated=Greatest('written', 'published'))
        self.assertEqual(articles.first().last_updated, now)

    @skipIfDBFeature('greatest_least_ignores_nulls')
    def test_propagates_null(self):
        """
        Tests if the `Greatest` function correctly propagates null values when annotating querysets.
        
        This test creates an `Article` instance with a non-null `written` field, then uses the `annotate` method with the `Greatest` function to add a new field `last_updated`. The test asserts that the `last_updated` field is `None` for the first article in the queryset, indicating that the `Greatest` function properly handles null values.
        
        Functions Used:
        """

        Article.objects.create(title='Testing with Django', written=timezone.now())
        articles = Article.objects.annotate(last_updated=Greatest('written', 'published'))
        self.assertIsNone(articles.first().last_updated)

    @skipIf(connection.vendor == 'mysql', "This doesn't work on MySQL")
    def test_coalesce_workaround(self):
        """
        Tests the coalesce workaround using Django's `Greatest` and `Coalesce` functions to determine the latest update time for an article. The function creates an article with a specific write date and then queries the database to find the latest of either the write or publish date, defaulting to a fixed past date if either is null. The expected result is that the first article's last updated timestamp matches its write date.
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
        """
        Tests the coalesce workaround for MySQL.
        
        This function creates an `Article` object with a specific title and current timestamp. It then uses RawSQL to create a past datetime object. The function annotates the queryset with a `last_updated` field using the `Greatest` and `Coalesce` functions, comparing the 'written' and 'published' fields with the past datetime. The expected result is that the first article's `last_updated` field should be set to the current timestamp.
        """

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
        Tests the behavior of the `Greatest` function when applied to `published` and `updated` fields on an `Article` object. Creates a new `Article` instance, annotates it with the latest of its `published` or `updated` timestamps using `Greatest`, and asserts that the `last_updated` field is `None`. This function uses the `Article` model, `timezone.now()`, and `Greatest` function from Django's ORM.
        """

        Article.objects.create(title='Testing with Django', written=timezone.now())
        articles = Article.objects.annotate(last_updated=Greatest('published', 'updated'))
        self.assertIsNone(articles.first().last_updated)

    def test_one_expressions(self):
        with self.assertRaisesMessage(ValueError, 'Greatest must take at least two expressions'):
            Greatest('written')

    def test_related_field(self):
        """
        Tests the functionality of a related field with the Greatest function. Creates an Author instance and a related Fan instance. Annotates the Author queryset with the highest age between the author's age and their fan's age using the Greatest function. Asserts that the highest age for the first author in the queryset is 50.
        """

        author = Author.objects.create(name='John Smith', age=45)
        Fan.objects.create(name='Margaret', age=50, author=author)
        authors = Author.objects.annotate(highest_age=Greatest('age', 'fans__age'))
        self.assertEqual(authors.first().highest_age, 50)

    def test_update(self):
        """
        Updates an author's alias by concatenating their name and goes_by fields.
        The function creates an author with the name 'James Smith' and goes_by 'Jim', then updates the author's alias using the Greatest function, which concatenates the name and goes_by fields. After updating, the author is refreshed from the database and the alias is expected to be 'Jim'.
        Args:
        None
        Returns:
        None
        """

        author = Author.objects.create(name='James Smith', goes_by='Jim')
        Author.objects.update(alias=Greatest('name', 'goes_by'))
        author.refresh_from_db()
        self.assertEqual(author.alias, 'Jim')

    def test_decimal_filter(self):
        """
        Tests the `Greatest` function filter for Decimal fields.
        
        This function creates an instance of `DecimalModel` with two decimal
        fields, `n1` and `n2`. It then annotates the queryset with the `greatest`
        value between `n1` and `n2`, and filters the queryset to find instances
        where the greatest value is equal to `1.2`.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        """

        obj = DecimalModel.objects.create(n1=Decimal('1.1'), n2=Decimal('1.2'))
        self.assertCountEqual(
            DecimalModel.objects.annotate(
                greatest=Greatest('n1', 'n2'),
            ).filter(greatest=Decimal('1.2')),
            [obj],
        )
