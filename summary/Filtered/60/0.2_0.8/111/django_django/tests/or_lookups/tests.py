from datetime import datetime
from operator import attrgetter

from django.db.models import Q
from django.test import TestCase

from .models import Article


class OrLookupsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the Article model.
        
        This method creates three instances of the Article model with different headlines and publication dates. The primary keys (pk) of the created articles are stored in the class attributes a1, a2, and a3.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Attributes:
        a1 (int): Primary key of the first Article instance.
        a2 (int): Primary key of the second Article instance.
        a3 (int): Primary key
        """

        cls.a1 = Article.objects.create(
            headline="Hello", pub_date=datetime(2005, 11, 27)
        ).pk
        cls.a2 = Article.objects.create(
            headline="Goodbye", pub_date=datetime(2005, 11, 28)
        ).pk
        cls.a3 = Article.objects.create(
            headline="Hello and goodbye", pub_date=datetime(2005, 11, 29)
        ).pk

    def test_filter_or(self):
        """
        Tests the functionality of the `|` operator in Django querysets for combining filters.
        
        This function asserts that the `|` operator correctly combines two querysets based on different filter conditions. It tests the following scenarios:
        1. Combining two querysets with different `startswith` conditions.
        2. Combining two querysets with `contains` conditions.
        3. Combining two querysets with an `iexact` condition and a `contains` condition.
        4. Combining two querysets using `
        """

        self.assertQuerySetEqual(
            (
                Article.objects.filter(headline__startswith="Hello")
                | Article.objects.filter(headline__startswith="Goodbye")
            ),
            ["Hello", "Goodbye", "Hello and goodbye"],
            attrgetter("headline"),
        )

        self.assertQuerySetEqual(
            Article.objects.filter(headline__contains="Hello")
            | Article.objects.filter(headline__contains="bye"),
            ["Hello", "Goodbye", "Hello and goodbye"],
            attrgetter("headline"),
        )

        self.assertQuerySetEqual(
            Article.objects.filter(headline__iexact="Hello")
            | Article.objects.filter(headline__contains="ood"),
            ["Hello", "Goodbye", "Hello and goodbye"],
            attrgetter("headline"),
        )

        self.assertQuerySetEqual(
            Article.objects.filter(
                Q(headline__startswith="Hello") | Q(headline__startswith="Goodbye")
            ),
            ["Hello", "Goodbye", "Hello and goodbye"],
            attrgetter("headline"),
        )

    def test_stages(self):
        # You can shorten this syntax with code like the following,  which is
        # especially useful if building the query in stages:
        articles = Article.objects.all()
        self.assertQuerySetEqual(
            articles.filter(headline__startswith="Hello")
            & articles.filter(headline__startswith="Goodbye"),
            [],
        )
        self.assertQuerySetEqual(
            articles.filter(headline__startswith="Hello")
            & articles.filter(headline__contains="bye"),
            ["Hello and goodbye"],
            attrgetter("headline"),
        )

    def test_pk_q(self):
        self.assertQuerySetEqual(
            Article.objects.filter(Q(pk=self.a1) | Q(pk=self.a2)),
            ["Hello", "Goodbye"],
            attrgetter("headline"),
        )

        self.assertQuerySetEqual(
            Article.objects.filter(Q(pk=self.a1) | Q(pk=self.a2) | Q(pk=self.a3)),
            ["Hello", "Goodbye", "Hello and goodbye"],
            attrgetter("headline"),
        )

    def test_pk_in(self):
        """
        Tests the filtering of articles based on primary key (pk) using the `__in` lookup.
        
        This function verifies that the `filter` method of the `Article` model's manager correctly filters articles based on their primary keys. The `__in` lookup is used to check if the primary key of the articles is in a given list or tuple of primary keys.
        
        Parameters:
        self (object): The test case instance.
        
        Returns:
        None: This function does not return any value. It
        """

        self.assertQuerySetEqual(
            Article.objects.filter(pk__in=[self.a1, self.a2, self.a3]),
            ["Hello", "Goodbye", "Hello and goodbye"],
            attrgetter("headline"),
        )

        self.assertQuerySetEqual(
            Article.objects.filter(pk__in=(self.a1, self.a2, self.a3)),
            ["Hello", "Goodbye", "Hello and goodbye"],
            attrgetter("headline"),
        )

        self.assertQuerySetEqual(
            Article.objects.filter(pk__in=[self.a1, self.a2, self.a3, 40000]),
            ["Hello", "Goodbye", "Hello and goodbye"],
            attrgetter("headline"),
        )

    def test_q_repr(self):
        or_expr = Q(baz=Article(headline="Foö"))
        self.assertEqual(repr(or_expr), "<Q: (AND: ('baz', <Article: Foö>))>")
        negated_or = ~Q(baz=Article(headline="Foö"))
        self.assertEqual(repr(negated_or), "<Q: (NOT (AND: ('baz', <Article: Foö>)))>")

    def test_q_negated(self):
        # Q objects can be negated
        self.assertQuerySetEqual(
            Article.objects.filter(Q(pk=self.a1) | ~Q(pk=self.a2)),
            ["Hello", "Hello and goodbye"],
            attrgetter("headline"),
        )

        self.assertQuerySetEqual(
            Article.objects.filter(~Q(pk=self.a1) & ~Q(pk=self.a2)),
            ["Hello and goodbye"],
            attrgetter("headline"),
        )
        # This allows for more complex queries than filter() and exclude()
        # alone would allow
        self.assertQuerySetEqual(
            Article.objects.filter(Q(pk=self.a1) & (~Q(pk=self.a2) | Q(pk=self.a3))),
            ["Hello"],
            attrgetter("headline"),
        )

    def test_complex_filter(self):
        # The 'complex_filter' method supports framework features such as
        # 'limit_choices_to' which normally take a single dictionary of lookup
        # arguments but need to support arbitrary queries via Q objects too.
        self.assertQuerySetEqual(
            Article.objects.complex_filter({"pk": self.a1}),
            ["Hello"],
            attrgetter("headline"),
        )

        self.assertQuerySetEqual(
            Article.objects.complex_filter(Q(pk=self.a1) | Q(pk=self.a2)),
            ["Hello", "Goodbye"],
            attrgetter("headline"),
        )

    def test_empty_in(self):
        """
        Tests the behavior of the `filter` method when using the `pk__in` lookup with an empty list.
        
        This function checks two scenarios:
        1. Passing an empty list to `pk__in` returns an empty query set.
        2. Using an OR condition with another query can return results even if the `pk__in` list is empty.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Points:
        - `filter(pk__in=[])`: Returns an empty query set if the
        """

        # Passing "in" an empty list returns no results ...
        self.assertQuerySetEqual(Article.objects.filter(pk__in=[]), [])
        # ... but can return results if we OR it with another query.
        self.assertQuerySetEqual(
            Article.objects.filter(Q(pk__in=[]) | Q(headline__icontains="goodbye")),
            ["Goodbye", "Hello and goodbye"],
            attrgetter("headline"),
        )

    def test_q_and(self):
        # Q arg objects are ANDed
        self.assertQuerySetEqual(
            Article.objects.filter(
                Q(headline__startswith="Hello"), Q(headline__contains="bye")
            ),
            ["Hello and goodbye"],
            attrgetter("headline"),
        )
        # Q arg AND order is irrelevant
        self.assertQuerySetEqual(
            Article.objects.filter(
                Q(headline__contains="bye"), headline__startswith="Hello"
            ),
            ["Hello and goodbye"],
            attrgetter("headline"),
        )

        self.assertQuerySetEqual(
            Article.objects.filter(
                Q(headline__startswith="Hello") & Q(headline__startswith="Goodbye")
            ),
            [],
        )

    def test_q_exclude(self):
        self.assertQuerySetEqual(
            Article.objects.exclude(Q(headline__startswith="Hello")),
            ["Goodbye"],
            attrgetter("headline"),
        )

    def test_other_arg_queries(self):
        """
        Tests for query arguments other than filter.
        
        This function tests various operations on query arguments, including:
        - Using `get` with multiple `Q` objects.
        - Using `filter` with logical operations (`|` and `&`).
        - Using `filter` with `values`.
        - Using `filter` with `in_bulk`.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - The function asserts the correctness of the query operations through various test cases.
        """

        # Try some arg queries with operations other than filter.
        self.assertEqual(
            Article.objects.get(
                Q(headline__startswith="Hello"), Q(headline__contains="bye")
            ).headline,
            "Hello and goodbye",
        )

        self.assertEqual(
            Article.objects.filter(
                Q(headline__startswith="Hello") | Q(headline__contains="bye")
            ).count(),
            3,
        )

        self.assertSequenceEqual(
            Article.objects.filter(
                Q(headline__startswith="Hello"), Q(headline__contains="bye")
            ).values(),
            [
                {
                    "headline": "Hello and goodbye",
                    "id": self.a3,
                    "pub_date": datetime(2005, 11, 29),
                },
            ],
        )

        self.assertEqual(
            Article.objects.filter(Q(headline__startswith="Hello")).in_bulk(
                [self.a1, self.a2]
            ),
            {self.a1: Article.objects.get(pk=self.a1)},
        )
