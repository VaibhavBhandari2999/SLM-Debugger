import datetime
from decimal import Decimal

from django.db.models import (
    Avg,
    Case,
    Count,
    Exists,
    F,
    Max,
    OuterRef,
    Q,
    StdDev,
    Subquery,
    Sum,
    Variance,
    When,
)
from django.test import TestCase
from django.test.utils import Approximate

from .models import Author, Book, Publisher


class FilteredAggregateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the Django application.
        
        This method creates and initializes several test objects for the Django application. It creates instances of the Author, Publisher, and Book models and establishes relationships between them. The method is intended to be used as a class method in a Django test case to provide a consistent set of test data for multiple test methods.
        
        Key Parameters:
        - None
        
        Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - None
        
        Returns:
        - None
        
        Side Effects:
        - Creates
        """

        cls.a1 = Author.objects.create(name="test", age=40)
        cls.a2 = Author.objects.create(name="test2", age=60)
        cls.a3 = Author.objects.create(name="test3", age=100)
        cls.p1 = Publisher.objects.create(
            name="Apress", num_awards=3, duration=datetime.timedelta(days=1)
        )
        cls.b1 = Book.objects.create(
            isbn="159059725",
            name="The Definitive Guide to Django: Web Development Done Right",
            pages=447,
            rating=4.5,
            price=Decimal("30.00"),
            contact=cls.a1,
            publisher=cls.p1,
            pubdate=datetime.date(2007, 12, 6),
        )
        cls.b2 = Book.objects.create(
            isbn="067232959",
            name="Sams Teach Yourself Django in 24 Hours",
            pages=528,
            rating=3.0,
            price=Decimal("23.09"),
            contact=cls.a2,
            publisher=cls.p1,
            pubdate=datetime.date(2008, 3, 3),
        )
        cls.b3 = Book.objects.create(
            isbn="159059996",
            name="Practical Django Projects",
            pages=600,
            rating=4.5,
            price=Decimal("29.69"),
            contact=cls.a3,
            publisher=cls.p1,
            pubdate=datetime.date(2008, 6, 23),
        )
        cls.a1.friends.add(cls.a2)
        cls.a1.friends.add(cls.a3)
        cls.b1.authors.add(cls.a1)
        cls.b1.authors.add(cls.a3)
        cls.b2.authors.add(cls.a2)
        cls.b3.authors.add(cls.a3)

    def test_filtered_aggregates(self):
        agg = Sum("age", filter=Q(name__startswith="test"))
        self.assertEqual(Author.objects.aggregate(age=agg)["age"], 200)

    def test_filtered_numerical_aggregates(self):
        """
        Tests the filtered numerical aggregates for the 'age' field in the Author model.
        
        This function iterates over a series of aggregate functions (Avg, StdDev, Variance) and their expected results. For each aggregate function, it applies a filter to only consider authors whose names start with 'test'. It then compares the result of the aggregate function on the filtered queryset to the expected result.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Parameters:
        - aggregate: The aggregate function to be tested
        """

        for aggregate, expected_result in (
            (Avg, Approximate(66.7, 1)),
            (StdDev, Approximate(24.9, 1)),
            (Variance, Approximate(622.2, 1)),
        ):
            with self.subTest(aggregate=aggregate.__name__):
                agg = aggregate("age", filter=Q(name__startswith="test"))
                self.assertEqual(
                    Author.objects.aggregate(age=agg)["age"], expected_result
                )

    def test_double_filtered_aggregates(self):
        agg = Sum("age", filter=Q(Q(name="test2") & ~Q(name="test")))
        self.assertEqual(Author.objects.aggregate(age=agg)["age"], 60)

    def test_excluded_aggregates(self):
        agg = Sum("age", filter=~Q(name="test2"))
        self.assertEqual(Author.objects.aggregate(age=agg)["age"], 140)

    def test_related_aggregates_m2m(self):
        agg = Sum("friends__age", filter=~Q(friends__name="test"))
        self.assertEqual(
            Author.objects.filter(name="test").aggregate(age=agg)["age"], 160
        )

    def test_related_aggregates_m2m_and_fk(self):
        q = Q(friends__book__publisher__name="Apress") & ~Q(friends__name="test3")
        agg = Sum("friends__book__pages", filter=q)
        self.assertEqual(
            Author.objects.filter(name="test").aggregate(pages=agg)["pages"], 528
        )

    def test_plain_annotate(self):
        agg = Sum("book__pages", filter=Q(book__rating__gt=3))
        qs = Author.objects.annotate(pages=agg).order_by("pk")
        self.assertSequenceEqual([a.pages for a in qs], [447, None, 1047])

    def test_filtered_aggregate_on_annotate(self):
        """
        Tests the filtered aggregate function on an annotated field.
        
        This function tests the behavior of the `aggregate` method when used with a filtered sum on an annotated field. The `annotate` method is used to sum the `pages` field from the related `book` model, but only for books with a rating greater than 3. This annotated field is then used in an aggregate function to sum the `age` field of the `Author` model, but only for authors whose total annotated pages are greater
        """

        pages_annotate = Sum("book__pages", filter=Q(book__rating__gt=3))
        age_agg = Sum("age", filter=Q(total_pages__gte=400))
        aggregated = Author.objects.annotate(total_pages=pages_annotate).aggregate(
            summed_age=age_agg
        )
        self.assertEqual(aggregated, {"summed_age": 140})

    def test_case_aggregate(self):
        agg = Sum(
            Case(When(friends__age=40, then=F("friends__age"))),
            filter=Q(friends__name__startswith="test"),
        )
        self.assertEqual(Author.objects.aggregate(age=agg)["age"], 80)

    def test_sum_star_exception(self):
        msg = "Star cannot be used with filter. Please specify a field."
        with self.assertRaisesMessage(ValueError, msg):
            Count("*", filter=Q(age=40))

    def test_filtered_reused_subquery(self):
        qs = Author.objects.annotate(
            older_friends_count=Count("friends", filter=Q(friends__age__gt=F("age"))),
        ).filter(
            older_friends_count__gte=2,
        )
        self.assertEqual(qs.get(pk__in=qs.values("pk")), self.a1)

    def test_filtered_aggregate_ref_annotation(self):
        aggs = Author.objects.annotate(double_age=F("age") * 2).aggregate(
            cnt=Count("pk", filter=Q(double_age__gt=100)),
        )
        self.assertEqual(aggs["cnt"], 2)

    def test_filtered_aggregate_ref_subquery_annotation(self):
        """
        Tests the filtered aggregate with a subquery and annotation.
        
        This function tests the functionality of an annotated field that uses a subquery to filter and aggregate data. Specifically, it annotates each author with the earliest book year they have written, and then counts the number of authors who have their earliest book published in the year 2008.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Concepts:
        - `annotate`: Adds a computed field to each object in the queryset.
        - `Sub
        """

        aggs = Author.objects.annotate(
            earliest_book_year=Subquery(
                Book.objects.filter(
                    contact__pk=OuterRef("pk"),
                )
                .order_by("pubdate")
                .values("pubdate__year")[:1]
            ),
        ).aggregate(
            cnt=Count("pk", filter=Q(earliest_book_year=2008)),
        )
        self.assertEqual(aggs["cnt"], 2)

    def test_filtered_aggregate_ref_multiple_subquery_annotation(self):
        """
        Tests the filtered aggregate with multiple subquery annotations.
        
        This function tests the use of filtered aggregate with multiple subquery annotations. It constructs a query that:
        - Filters books by their publisher.
        - Annotates each publisher with:
        - `has_authors`: a boolean indicating if the book has any authors.
        - `authors_have_other_books`: a boolean indicating if any of the book's authors have written other books.
        - Aggregates the maximum rating of books that meet the following conditions:
        """

        aggregate = (
            Book.objects.values("publisher")
            .annotate(
                has_authors=Exists(
                    Book.authors.through.objects.filter(book=OuterRef("pk")),
                ),
                authors_have_other_books=Exists(
                    Book.objects.filter(
                        authors__in=Author.objects.filter(
                            book_contact_set=OuterRef(OuterRef("pk")),
                        )
                    ).exclude(pk=OuterRef("pk")),
                ),
            )
            .aggregate(
                max_rating=Max(
                    "rating",
                    filter=Q(has_authors=True, authors_have_other_books=False),
                )
            )
        )
        self.assertEqual(aggregate, {"max_rating": 4.5})

    def test_filtered_aggregate_on_exists(self):
        aggregate = Book.objects.values("publisher").aggregate(
            max_rating=Max(
                "rating",
                filter=Exists(
                    Book.authors.through.objects.filter(book=OuterRef("pk")),
                ),
            ),
        )
        self.assertEqual(aggregate, {"max_rating": 4.5})

    def test_filtered_aggregate_empty_condition(self):
        book = Book.objects.annotate(
            authors_count=Count(
                "authors",
                filter=Q(authors__in=[]),
            ),
        ).get(pk=self.b1.pk)
        self.assertEqual(book.authors_count, 0)
        aggregate = Book.objects.aggregate(
            max_rating=Max("rating", filter=Q(rating__in=[]))
        )
        self.assertEqual(aggregate, {"max_rating": None})

    def test_filtered_aggregate_full_condition(self):
        book = Book.objects.annotate(
            authors_count=Count(
                "authors",
                filter=~Q(authors__in=[]),
            ),
        ).get(pk=self.b1.pk)
        self.assertEqual(book.authors_count, 2)
        aggregate = Book.objects.aggregate(
            max_rating=Max("rating", filter=~Q(rating__in=[]))
        )
        self.assertEqual(aggregate, {"max_rating": 4.5})
