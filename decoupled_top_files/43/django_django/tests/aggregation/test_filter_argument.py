import datetime
from decimal import Decimal

from django.db.models import (
    Avg, Case, Count, F, OuterRef, Q, StdDev, Subquery, Sum, Variance, When,
)
from django.test import TestCase
from django.test.utils import Approximate

from .models import Author, Book, Publisher


class FilteredAggregateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the Django application.
        
        This method creates instances of `Author`, `Publisher`, and `Book` models and establishes relationships between them. It also adds friends and authors to the books.
        
        Important Functions:
        - `Author.objects.create()`: Creates an author instance with specified name and age.
        - `Publisher.objects.create()`: Creates a publisher instance with specified name and duration.
        - `Book.objects.create()`: Creates a book instance with specified ISBN, name,
        """

        cls.a1 = Author.objects.create(name='test', age=40)
        cls.a2 = Author.objects.create(name='test2', age=60)
        cls.a3 = Author.objects.create(name='test3', age=100)
        cls.p1 = Publisher.objects.create(name='Apress', num_awards=3, duration=datetime.timedelta(days=1))
        cls.b1 = Book.objects.create(
            isbn='159059725', name='The Definitive Guide to Django: Web Development Done Right',
            pages=447, rating=4.5, price=Decimal('30.00'), contact=cls.a1, publisher=cls.p1,
            pubdate=datetime.date(2007, 12, 6),
        )
        cls.b2 = Book.objects.create(
            isbn='067232959', name='Sams Teach Yourself Django in 24 Hours',
            pages=528, rating=3.0, price=Decimal('23.09'), contact=cls.a2, publisher=cls.p1,
            pubdate=datetime.date(2008, 3, 3),
        )
        cls.b3 = Book.objects.create(
            isbn='159059996', name='Practical Django Projects',
            pages=600, rating=4.5, price=Decimal('29.69'), contact=cls.a3, publisher=cls.p1,
            pubdate=datetime.date(2008, 6, 23),
        )
        cls.a1.friends.add(cls.a2)
        cls.a1.friends.add(cls.a3)
        cls.b1.authors.add(cls.a1)
        cls.b1.authors.add(cls.a3)
        cls.b2.authors.add(cls.a2)
        cls.b3.authors.add(cls.a3)

    def test_filtered_aggregates(self):
        agg = Sum('age', filter=Q(name__startswith='test'))
        self.assertEqual(Author.objects.aggregate(age=agg)['age'], 200)

    def test_filtered_numerical_aggregates(self):
        """
        Tests filtered numerical aggregates on the 'Author' model.
        
        This function verifies that the aggregation of numerical data, such as average age, standard deviation, and variance,
        is correctly applied with a filter. The filter is defined using Django's Q object to select authors whose names start
        with 'test'. The expected results for these aggregations are compared against the actual results obtained from the
        database.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        -
        """

        for aggregate, expected_result in (
            (Avg, Approximate(66.7, 1)),
            (StdDev, Approximate(24.9, 1)),
            (Variance, Approximate(622.2, 1)),
        ):
            with self.subTest(aggregate=aggregate.__name__):
                agg = aggregate('age', filter=Q(name__startswith='test'))
                self.assertEqual(Author.objects.aggregate(age=agg)['age'], expected_result)

    def test_double_filtered_aggregates(self):
        agg = Sum('age', filter=Q(Q(name='test2') & ~Q(name='test')))
        self.assertEqual(Author.objects.aggregate(age=agg)['age'], 60)

    def test_excluded_aggregates(self):
        agg = Sum('age', filter=~Q(name='test2'))
        self.assertEqual(Author.objects.aggregate(age=agg)['age'], 140)

    def test_related_aggregates_m2m(self):
        agg = Sum('friends__age', filter=~Q(friends__name='test'))
        self.assertEqual(Author.objects.filter(name='test').aggregate(age=agg)['age'], 160)

    def test_related_aggregates_m2m_and_fk(self):
        """
        Tests the aggregation of related fields using M2M and FK relationships. Filters authors with friends who have books published by 'Apress' and excludes friends named 'test3'. Aggregates the sum of pages from these filtered books. The input is an Author object with the name 'test', and the output is the sum of book pages (expected: 528).
        """

        q = Q(friends__book__publisher__name='Apress') & ~Q(friends__name='test3')
        agg = Sum('friends__book__pages', filter=q)
        self.assertEqual(Author.objects.filter(name='test').aggregate(pages=agg)['pages'], 528)

    def test_plain_annotate(self):
        """
        Annotates each author with the sum of pages of their books that have a rating greater than 3. The resulting queryset is ordered by author primary key (pk). The output is a list of the annotated page counts, where `None` indicates no qualifying books.
        """

        agg = Sum('book__pages', filter=Q(book__rating__gt=3))
        qs = Author.objects.annotate(pages=agg).order_by('pk')
        self.assertSequenceEqual([a.pages for a in qs], [447, None, 1047])

    def test_filtered_aggregate_on_annotate(self):
        """
        Tests the filtered aggregate on annotate functionality.
        
        This function uses `Sum` aggregation with filters (`Q`) to calculate the sum of annotated fields. It first annotates the `Author` objects with the total number of pages from their books where the book's rating is greater than 3. Then, it aggregates these annotated values to find the sum of ages where the total pages are greater than or equal to 400. The expected result is a dictionary containing the summed age, which should be
        """

        pages_annotate = Sum('book__pages', filter=Q(book__rating__gt=3))
        age_agg = Sum('age', filter=Q(total_pages__gte=400))
        aggregated = Author.objects.annotate(total_pages=pages_annotate).aggregate(summed_age=age_agg)
        self.assertEqual(aggregated, {'summed_age': 140})

    def test_case_aggregate(self):
        """
        Aggregate the sum of friends' age where the friend's age is 40 and their name starts with 'test'. The function uses the `Sum` and `Case` functions from Django's ORM to perform the aggregation. The result is filtered based on the condition that the friend's name starts with 'test'. The expected output is the sum of ages, which should be 80.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        None
        
        Example:
        """

        agg = Sum(
            Case(When(friends__age=40, then=F('friends__age'))),
            filter=Q(friends__name__startswith='test'),
        )
        self.assertEqual(Author.objects.aggregate(age=agg)['age'], 80)

    def test_sum_star_exception(self):
        """
        Test that using the '*' star symbol with a filter raises a ValueError with the appropriate message.
        
        This function checks if attempting to use the '*' star symbol in a Count query along with a filter
        results in a ValueError being raised with the expected error message.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the '*' star symbol is used with a filter in a Count query, a ValueError should be raised with the message 'Star cannot be used with filter
        """

        msg = 'Star cannot be used with filter. Please specify a field.'
        with self.assertRaisesMessage(ValueError, msg):
            Count('*', filter=Q(age=40))

    def test_filtered_reused_subquery(self):
        """
        Tests filtering and reusing a subquery that counts friends older than the author. The function annotates each author with the count of their friends who are older, then filters authors based on this count. The input is an Author queryset, and the output is a filtered queryset of authors with at least two older friends.
        """

        qs = Author.objects.annotate(
            older_friends_count=Count('friends', filter=Q(friends__age__gt=F('age'))),
        ).filter(
            older_friends_count__gte=2,
        )
        self.assertEqual(qs.get(pk__in=qs.values('pk')), self.a1)

    def test_filtered_aggregate_ref_annotation(self):
        """
        Tests the filtered aggregate functionality using the `annotate` and `aggregate` methods on an Author queryset. The `double_age` annotation is created by multiplying the 'age' field by 2, and the aggregate counts the number of authors where `double_age` is greater than 100. The expected count is 2.
        """

        aggs = Author.objects.annotate(
            double_age=F('age') * 2,
        ).aggregate(
            cnt=Count('pk', filter=Q(double_age__gt=100)),
        )
        self.assertEqual(aggs['cnt'], 2)

    def test_filtered_aggregate_ref_subquery_annotation(self):
        """
        Tests filtering and aggregating based on a subquery that annotates with the earliest book year for each author. The function uses Subquery, OuterRef, Filter, and Count to count authors whose earliest book year is 2008.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - Subquery: Used to create a subquery that retrieves the earliest publication year of books associated with each author.
        - OuterRef: References the outer query's field
        """

        aggs = Author.objects.annotate(
            earliest_book_year=Subquery(
                Book.objects.filter(
                    contact__pk=OuterRef('pk'),
                ).order_by('pubdate').values('pubdate__year')[:1]
            ),
        ).aggregate(
            cnt=Count('pk', filter=Q(earliest_book_year=2008)),
        )
        self.assertEqual(aggs['cnt'], 2)
