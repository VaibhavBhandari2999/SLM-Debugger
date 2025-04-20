from datetime import datetime
from operator import attrgetter

from django.db.models import Q
from django.test import TestCase

from .models import Article


class OrLookupsTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.a1 = Article.objects.create(
            headline='Hello', pub_date=datetime(2005, 11, 27)
        ).pk
        cls.a2 = Article.objects.create(
            headline='Goodbye', pub_date=datetime(2005, 11, 28)
        ).pk
        cls.a3 = Article.objects.create(
            headline='Hello and goodbye', pub_date=datetime(2005, 11, 29)
        ).pk

    def test_filter_or(self):
        """
        Tests the functionality of filtering querysets using the OR operator.
        
        This function tests various scenarios where querysets are combined using the OR operator. The tests check for different conditions such as case sensitivity, containment, and the use of Q objects. The expected results are compared against the actual results using the assertQuerysetEqual method.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Points:
        - Filters articles based on the headline starting with 'Hello' or 'Goodbye'.
        - Filters articles based on the
        """

        self.assertQuerysetEqual(
            (
                Article.objects.filter(headline__startswith='Hello') |
                Article.objects.filter(headline__startswith='Goodbye')
            ), [
                'Hello',
                'Goodbye',
                'Hello and goodbye'
            ],
            attrgetter("headline")
        )

        self.assertQuerysetEqual(
            Article.objects.filter(headline__contains='Hello') | Article.objects.filter(headline__contains='bye'), [
                'Hello',
                'Goodbye',
                'Hello and goodbye'
            ],
            attrgetter("headline")
        )

        self.assertQuerysetEqual(
            Article.objects.filter(headline__iexact='Hello') | Article.objects.filter(headline__contains='ood'), [
                'Hello',
                'Goodbye',
                'Hello and goodbye'
            ],
            attrgetter("headline")
        )

        self.assertQuerysetEqual(
            Article.objects.filter(Q(headline__startswith='Hello') | Q(headline__startswith='Goodbye')), [
                'Hello',
                'Goodbye',
                'Hello and goodbye'
            ],
            attrgetter("headline")
        )

    def test_stages(self):
        """
        Tests the filtering of articles based on their headlines.
        
        This function tests the filtering of articles in the database using the `filter` method of the `Article` model's `objects` manager. The tests are performed in stages, where the articles are first filtered based on specific conditions and then combined using the `&` operator. The function asserts that the resulting queryset matches the expected output.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Operations:
        - `articles.filter(headline__startswith='
        """

        # You can shorten this syntax with code like the following,  which is
        # especially useful if building the query in stages:
        articles = Article.objects.all()
        self.assertQuerysetEqual(
            articles.filter(headline__startswith='Hello') & articles.filter(headline__startswith='Goodbye'),
            []
        )
        self.assertQuerysetEqual(
            articles.filter(headline__startswith='Hello') & articles.filter(headline__contains='bye'), [
                'Hello and goodbye'
            ],
            attrgetter("headline")
        )

    def test_pk_q(self):
        self.assertQuerysetEqual(
            Article.objects.filter(Q(pk=self.a1) | Q(pk=self.a2)), [
                'Hello',
                'Goodbye'
            ],
            attrgetter("headline")
        )

        self.assertQuerysetEqual(
            Article.objects.filter(Q(pk=self.a1) | Q(pk=self.a2) | Q(pk=self.a3)), [
                'Hello',
                'Goodbye',
                'Hello and goodbye'
            ],
            attrgetter("headline"),
        )

    def test_pk_in(self):
        self.assertQuerysetEqual(
            Article.objects.filter(pk__in=[self.a1, self.a2, self.a3]), [
                'Hello',
                'Goodbye',
                'Hello and goodbye'
            ],
            attrgetter("headline"),
        )

        self.assertQuerysetEqual(
            Article.objects.filter(pk__in=(self.a1, self.a2, self.a3)), [
                'Hello',
                'Goodbye',
                'Hello and goodbye'
            ],
            attrgetter("headline"),
        )

        self.assertQuerysetEqual(
            Article.objects.filter(pk__in=[self.a1, self.a2, self.a3, 40000]), [
                'Hello',
                'Goodbye',
                'Hello and goodbye'
            ],
            attrgetter("headline"),
        )

    def test_q_repr(self):
        """
        Test the representation of a Q object.
        
        This function checks the string representation of a Q object and its negation. The Q object is used to represent a query in Django, and the test ensures that the representation is as expected.
        
        Parameters:
        or_expr (Q): A Q object representing an AND query with a specific attribute and value.
        negated_or (Q): A negated Q object representing a NOT query with a specific attribute and value.
        
        Returns:
        None: This function is used
        """

        or_expr = Q(baz=Article(headline="Foö"))
        self.assertEqual(repr(or_expr), "<Q: (AND: ('baz', <Article: Foö>))>")
        negated_or = ~Q(baz=Article(headline="Foö"))
        self.assertEqual(repr(negated_or), "<Q: (NOT (AND: ('baz', <Article: Foö>)))>")

    def test_q_negated(self):
        # Q objects can be negated
        self.assertQuerysetEqual(
            Article.objects.filter(Q(pk=self.a1) | ~Q(pk=self.a2)), [
                'Hello',
                'Hello and goodbye'
            ],
            attrgetter("headline")
        )

        self.assertQuerysetEqual(
            Article.objects.filter(~Q(pk=self.a1) & ~Q(pk=self.a2)), [
                'Hello and goodbye'
            ],
            attrgetter("headline"),
        )
        # This allows for more complex queries than filter() and exclude()
        # alone would allow
        self.assertQuerysetEqual(
            Article.objects.filter(Q(pk=self.a1) & (~Q(pk=self.a2) | Q(pk=self.a3))), [
                'Hello'
            ],
            attrgetter("headline"),
        )

    def test_complex_filter(self):
        """
        Tests the 'complex_filter' method, which supports filtering based on complex queries using dictionaries or Q objects. The method is capable of handling 'limit_choices_to' framework features.
        
        Parameters:
        - self: The test case instance.
        
        Returns:
        - None: This function asserts the expected results against the actual querysets returned by the 'complex_filter' method.
        
        Key Points:
        - The method supports filtering with a single dictionary of lookup arguments.
        - It also supports filtering with Q objects for more complex queries.
        -
        """

        # The 'complex_filter' method supports framework features such as
        # 'limit_choices_to' which normally take a single dictionary of lookup
        # arguments but need to support arbitrary queries via Q objects too.
        self.assertQuerysetEqual(
            Article.objects.complex_filter({'pk': self.a1}), [
                'Hello'
            ],
            attrgetter("headline"),
        )

        self.assertQuerysetEqual(
            Article.objects.complex_filter(Q(pk=self.a1) | Q(pk=self.a2)), [
                'Hello',
                'Goodbye'
            ],
            attrgetter("headline"),
        )

    def test_empty_in(self):
        # Passing "in" an empty list returns no results ...
        self.assertQuerysetEqual(
            Article.objects.filter(pk__in=[]),
            []
        )
        # ... but can return results if we OR it with another query.
        self.assertQuerysetEqual(
            Article.objects.filter(Q(pk__in=[]) | Q(headline__icontains='goodbye')), [
                'Goodbye',
                'Hello and goodbye'
            ],
            attrgetter("headline"),
        )

    def test_q_and(self):
        """
        Tests the AND operation between Q objects in a Django queryset filter.
        
        This function verifies that:
        1. Q objects are ANDed when passed as separate arguments to the filter method.
        2. The order of Q objects in the filter method does not affect the result.
        3. An empty queryset is returned when the conditions specified in the Q objects are mutually exclusive.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The queryset returned by the filter method matches the expected headlines when using separate Q
        """

        # Q arg objects are ANDed
        self.assertQuerysetEqual(
            Article.objects.filter(Q(headline__startswith='Hello'), Q(headline__contains='bye')), [
                'Hello and goodbye'
            ],
            attrgetter("headline")
        )
        # Q arg AND order is irrelevant
        self.assertQuerysetEqual(
            Article.objects.filter(Q(headline__contains='bye'), headline__startswith='Hello'), [
                'Hello and goodbye'
            ],
            attrgetter("headline"),
        )

        self.assertQuerysetEqual(
            Article.objects.filter(Q(headline__startswith='Hello') & Q(headline__startswith='Goodbye')),
            []
        )

    def test_q_exclude(self):
        self.assertQuerysetEqual(
            Article.objects.exclude(Q(headline__startswith='Hello')), [
                'Goodbye'
            ],
            attrgetter("headline")
        )

    def test_other_arg_queries(self):
        """
        Tests the functionality of various query operations on the Article model.
        
        This function tests several aspects of query operations on the Article model:
        - Retrieving an object using multiple `Q` objects with different operations.
        - Filtering articles using logical OR and counting the results.
        - Filtering articles using multiple `Q` objects and checking the values.
        - Filtering articles and using `in_bulk` to retrieve specific instances.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Operations:
        - `get`: Retrieves a single object
        """

        # Try some arg queries with operations other than filter.
        self.assertEqual(
            Article.objects.get(Q(headline__startswith='Hello'), Q(headline__contains='bye')).headline,
            'Hello and goodbye'
        )

        self.assertEqual(
            Article.objects.filter(Q(headline__startswith='Hello') | Q(headline__contains='bye')).count(),
            3
        )

        self.assertSequenceEqual(
            Article.objects.filter(Q(headline__startswith='Hello'), Q(headline__contains='bye')).values(), [
                {"headline": "Hello and goodbye", "id": self.a3, "pub_date": datetime(2005, 11, 29)},
            ],
        )

        self.assertEqual(
            Article.objects.filter(Q(headline__startswith='Hello')).in_bulk([self.a1, self.a2]),
            {self.a1: Article.objects.get(pk=self.a1)}
        )
