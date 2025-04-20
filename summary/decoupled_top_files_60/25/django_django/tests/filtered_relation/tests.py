from unittest import mock

from django.db import connection, transaction
from django.db.models import Case, Count, F, FilteredRelation, Q, When
from django.test import TestCase
from django.test.testcases import skipUnlessDBFeature

from .models import Author, Book, Borrower, Editor, RentalSession, Reservation


class FilteredRelationTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the book management system.
        
        This method creates a set of test data for use in unit tests. It creates instances of the `Author` and `Editor` models, and related `Book` instances. The data includes multiple authors, editors, and books, with some books having multiple authors and favorite books associated with certain authors.
        
        Key Parameters:
        - None (This method uses class-level attributes to store the created data).
        
        Keywords:
        - None
        
        Inputs:
        - None
        
        Outputs:
        """

        cls.author1 = Author.objects.create(name='Alice')
        cls.author2 = Author.objects.create(name='Jane')
        cls.editor_a = Editor.objects.create(name='a')
        cls.editor_b = Editor.objects.create(name='b')
        cls.book1 = Book.objects.create(
            title='Poem by Alice',
            editor=cls.editor_a,
            author=cls.author1,
        )
        cls.book1.generic_author.set([cls.author2])
        cls.book2 = Book.objects.create(
            title='The book by Jane A',
            editor=cls.editor_b,
            author=cls.author2,
        )
        cls.book3 = Book.objects.create(
            title='The book by Jane B',
            editor=cls.editor_b,
            author=cls.author2,
        )
        cls.book4 = Book.objects.create(
            title='The book by Alice',
            editor=cls.editor_a,
            author=cls.author1,
        )
        cls.author1.favorite_books.add(cls.book2)
        cls.author1.favorite_books.add(cls.book3)

    def test_select_related(self):
        qs = Author.objects.annotate(
            book_join=FilteredRelation('book'),
        ).select_related('book_join__editor').order_by('pk', 'book_join__pk')
        with self.assertNumQueries(1):
            self.assertQuerysetEqual(qs, [
                (self.author1, self.book1, self.editor_a, self.author1),
                (self.author1, self.book4, self.editor_a, self.author1),
                (self.author2, self.book2, self.editor_b, self.author2),
                (self.author2, self.book3, self.editor_b, self.author2),
            ], lambda x: (x, x.book_join, x.book_join.editor, x.book_join.author))

    def test_select_related_multiple(self):
        """
        Tests the functionality of the `select_related` method when used with multiple `FilteredRelation` annotations.
        
        This method creates a queryset of books and annotates each book with its author and editor using `FilteredRelation`. It then uses `select_related` to fetch the related author and editor objects in a single query. The resulting queryset is ordered by primary key.
        
        Parameters:
        - None
        
        Returns:
        - A queryset of books with their related author and editor objects fetched using a single query.
        
        Expected Output:
        -
        """

        qs = Book.objects.annotate(
            author_join=FilteredRelation('author'),
            editor_join=FilteredRelation('editor'),
        ).select_related('author_join', 'editor_join').order_by('pk')
        self.assertQuerysetEqual(qs, [
            (self.book1, self.author1, self.editor_a),
            (self.book2, self.author2, self.editor_b),
            (self.book3, self.author2, self.editor_b),
            (self.book4, self.author1, self.editor_a),
        ], lambda x: (x, x.author_join, x.editor_join))

    def test_select_related_with_empty_relation(self):
        qs = Author.objects.annotate(
            book_join=FilteredRelation('book', condition=Q(pk=-1)),
        ).select_related('book_join').order_by('pk')
        self.assertSequenceEqual(qs, [self.author1, self.author2])

    def test_select_related_foreign_key(self):
        qs = Book.objects.annotate(
            author_join=FilteredRelation('author'),
        ).select_related('author_join').order_by('pk')
        with self.assertNumQueries(1):
            self.assertQuerysetEqual(qs, [
                (self.book1, self.author1),
                (self.book2, self.author2),
                (self.book3, self.author2),
                (self.book4, self.author1),
            ], lambda x: (x, x.author_join))

    @skipUnlessDBFeature('has_select_for_update', 'has_select_for_update_of')
    def test_select_related_foreign_key_for_update_of(self):
        """
        Tests the behavior of `select_related` and `select_for_update` methods when used together with a `FilteredRelation` on a foreign key field.
        
        This method ensures that the queryset is properly optimized to perform a single database query and locks the selected objects for update.
        
        Parameters:
        - None (The method uses instance attributes `self.book1`, `self.book2`, `self.book3`, `self.book4`, `self.author1`, and `self.author2` which are assumed to be set
        """

        with transaction.atomic():
            qs = Book.objects.annotate(
                author_join=FilteredRelation('author'),
            ).select_related('author_join').select_for_update(of=('self',)).order_by('pk')
            with self.assertNumQueries(1):
                self.assertQuerysetEqual(qs, [
                    (self.book1, self.author1),
                    (self.book2, self.author2),
                    (self.book3, self.author2),
                    (self.book4, self.author1),
                ], lambda x: (x, x.author_join))

    def test_without_join(self):
        self.assertSequenceEqual(
            Author.objects.annotate(
                book_alice=FilteredRelation('book', condition=Q(book__title__iexact='poem by alice')),
            ),
            [self.author1, self.author2]
        )

    def test_with_join(self):
        self.assertSequenceEqual(
            Author.objects.annotate(
                book_alice=FilteredRelation('book', condition=Q(book__title__iexact='poem by alice')),
            ).filter(book_alice__isnull=False),
            [self.author1]
        )

    def test_with_exclude(self):
        self.assertSequenceEqual(
            Author.objects.annotate(
                book_alice=FilteredRelation('book', condition=Q(book__title__iexact='poem by alice')),
            ).exclude(book_alice__isnull=False),
            [self.author2],
        )

    def test_with_join_and_complex_condition(self):
        """
        Tests filtering authors based on complex conditions involving their books.
        
        This function asserts that the query returns a sequence containing only the author with the specified conditions:
        - The author has a book titled 'poem by alice' (case-insensitive).
        - The author has a book with a state of 'RENTED'.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Assertions:
        - The sequence of authors returned by the query should contain exactly one author: self.author1.
        - The returned author should have
        """

        self.assertSequenceEqual(
            Author.objects.annotate(
                book_alice=FilteredRelation(
                    'book', condition=Q(
                        Q(book__title__iexact='poem by alice') |
                        Q(book__state=Book.RENTED)
                    ),
                ),
            ).filter(book_alice__isnull=False),
            [self.author1]
        )

    def test_internal_queryset_alias_mapping(self):
        queryset = Author.objects.annotate(
            book_alice=FilteredRelation('book', condition=Q(book__title__iexact='poem by alice')),
        ).filter(book_alice__isnull=False)
        self.assertIn(
            'INNER JOIN {} book_alice ON'.format(connection.ops.quote_name('filtered_relation_book')),
            str(queryset.query)
        )

    def test_with_multiple_filter(self):
        """
        Tests filtering authors based on multiple conditions.
        
        This function filters authors who have edited a book with a specific title and editor. The filtering is done using the `FilteredRelation` method, which allows for complex queries to be executed efficiently. The function asserts that the filtered result contains only the expected author.
        
        Parameters:
        - None (the function uses pre-defined objects and queries)
        
        Returns:
        - None (the function asserts the result)
        
        Key Details:
        - `FilteredRelation`: Used to filter the related 'book'
        """

        self.assertSequenceEqual(
            Author.objects.annotate(
                book_editor_a=FilteredRelation(
                    'book',
                    condition=Q(book__title__icontains='book', book__editor_id=self.editor_a.pk),
                ),
            ).filter(book_editor_a__isnull=False),
            [self.author1]
        )

    def test_multiple_times(self):
        self.assertSequenceEqual(
            Author.objects.annotate(
                book_title_alice=FilteredRelation('book', condition=Q(book__title__icontains='alice')),
            ).filter(book_title_alice__isnull=False).filter(book_title_alice__isnull=False).distinct(),
            [self.author1]
        )

    def test_exclude_relation_with_join(self):
        """
        Tests the exclusion of a relation with a join in Django ORM.
        
        This function asserts that the filtered relation, excluding books with the title containing 'alice', is correctly applied and returns the expected author.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - The result of the query should match the author with id 'self.author2'.
        """

        self.assertSequenceEqual(
            Author.objects.annotate(
                book_alice=FilteredRelation('book', condition=~Q(book__title__icontains='alice')),
            ).filter(book_alice__isnull=False).distinct(),
            [self.author2]
        )

    def test_with_m2m(self):
        qs = Author.objects.annotate(
            favorite_books_written_by_jane=FilteredRelation(
                'favorite_books', condition=Q(favorite_books__in=[self.book2]),
            ),
        ).filter(favorite_books_written_by_jane__isnull=False)
        self.assertSequenceEqual(qs, [self.author1])

    def test_with_m2m_deep(self):
        qs = Author.objects.annotate(
            favorite_books_written_by_jane=FilteredRelation(
                'favorite_books', condition=Q(favorite_books__author=self.author2),
            ),
        ).filter(favorite_books_written_by_jane__title='The book by Jane B')
        self.assertSequenceEqual(qs, [self.author1])

    def test_with_m2m_multijoin(self):
        """
        Function: test_with_m2m_multijoin
        
        This function tests a query involving multiple joins and a filtered relation on a Many-to-Many (M2M) relationship.
        
        Parameters:
        - self: The test case instance (typically used in unit tests).
        
        Returns:
        - A QuerySet of Author objects that have favorite books written by a specific author (self.author2) and edited by a person named 'b'.
        
        Key Steps:
        1. Annotates the QuerySet with a filtered relation
        """

        qs = Author.objects.annotate(
            favorite_books_written_by_jane=FilteredRelation(
                'favorite_books', condition=Q(favorite_books__author=self.author2),
            )
        ).filter(favorite_books_written_by_jane__editor__name='b').distinct()
        self.assertSequenceEqual(qs, [self.author1])

    def test_values_list(self):
        self.assertSequenceEqual(
            Author.objects.annotate(
                book_alice=FilteredRelation('book', condition=Q(book__title__iexact='poem by alice')),
            ).filter(book_alice__isnull=False).values_list('book_alice__title', flat=True),
            ['Poem by Alice']
        )

    def test_values(self):
        """
        Tests the filtering of authors based on a specific book title using the FilteredRelation function.
        
        This function asserts that the filtered and annotated query set of authors contains only the author named 'Alice' who has a book titled 'poem by alice'.
        
        Parameters:
        - None (the function relies on pre-defined objects: self.author1, which is an instance of Author with name 'Alice')
        
        Returns:
        - None (the function asserts the correctness of the query set)
        
        Key Concepts:
        - FilteredRelation:
        """

        self.assertSequenceEqual(
            Author.objects.annotate(
                book_alice=FilteredRelation('book', condition=Q(book__title__iexact='poem by alice')),
            ).filter(book_alice__isnull=False).values(),
            [{'id': self.author1.pk, 'name': 'Alice', 'content_type_id': None, 'object_id': None}]
        )

    def test_extra(self):
        self.assertSequenceEqual(
            Author.objects.annotate(
                book_alice=FilteredRelation('book', condition=Q(book__title__iexact='poem by alice')),
            ).filter(book_alice__isnull=False).extra(where=['1 = 1']),
            [self.author1]
        )

    @skipUnlessDBFeature('supports_select_union')
    def test_union(self):
        qs1 = Author.objects.annotate(
            book_alice=FilteredRelation('book', condition=Q(book__title__iexact='poem by alice')),
        ).filter(book_alice__isnull=False)
        qs2 = Author.objects.annotate(
            book_jane=FilteredRelation('book', condition=Q(book__title__iexact='the book by jane a')),
        ).filter(book_jane__isnull=False)
        self.assertSequenceEqual(qs1.union(qs2), [self.author1, self.author2])

    @skipUnlessDBFeature('supports_select_intersection')
    def test_intersection(self):
        """
        Function: test_intersection
        
        This function tests the intersection of two query sets (qs1 and qs2) that are filtered based on specific conditions.
        
        Parameters:
        - self: The object instance that the method is bound to.
        
        Key Parameters:
        - qs1: The first queryset that is annotated with a FilteredRelation for books titled 'poem by alice' and filtered to exclude authors without such a book.
        - qs2: The second queryset that is annotated with a FilteredRelation for books titled
        """

        qs1 = Author.objects.annotate(
            book_alice=FilteredRelation('book', condition=Q(book__title__iexact='poem by alice')),
        ).filter(book_alice__isnull=False)
        qs2 = Author.objects.annotate(
            book_jane=FilteredRelation('book', condition=Q(book__title__iexact='the book by jane a')),
        ).filter(book_jane__isnull=False)
        self.assertSequenceEqual(qs1.intersection(qs2), [])

    @skipUnlessDBFeature('supports_select_difference')
    def test_difference(self):
        """
        Function: test_difference
        
        This function tests the difference between two querysets of authors based on specific book titles.
        
        Parameters:
        - self: The current test case instance.
        
        Key Parameters:
        - qs1: A queryset of authors annotated with a filtered relation for books titled 'poem by alice'.
        - qs2: A queryset of authors annotated with a filtered relation for books titled 'the book by jane a'.
        
        Keywords:
        - None
        
        Returns:
        - A list of authors who have a book titled '
        """

        qs1 = Author.objects.annotate(
            book_alice=FilteredRelation('book', condition=Q(book__title__iexact='poem by alice')),
        ).filter(book_alice__isnull=False)
        qs2 = Author.objects.annotate(
            book_jane=FilteredRelation('book', condition=Q(book__title__iexact='the book by jane a')),
        ).filter(book_jane__isnull=False)
        self.assertSequenceEqual(qs1.difference(qs2), [self.author1])

    def test_select_for_update(self):
        self.assertSequenceEqual(
            Author.objects.annotate(
                book_jane=FilteredRelation('book', condition=Q(book__title__iexact='the book by jane a')),
            ).filter(book_jane__isnull=False).select_for_update(),
            [self.author2]
        )

    def test_defer(self):
        # One query for the list and one query for the deferred title.
        with self.assertNumQueries(2):
            self.assertQuerysetEqual(
                Author.objects.annotate(
                    book_alice=FilteredRelation('book', condition=Q(book__title__iexact='poem by alice')),
                ).filter(book_alice__isnull=False).select_related('book_alice').defer('book_alice__title'),
                ['Poem by Alice'], lambda author: author.book_alice.title
            )

    def test_only_not_supported(self):
        msg = 'only() is not supported with FilteredRelation.'
        with self.assertRaisesMessage(ValueError, msg):
            Author.objects.annotate(
                book_alice=FilteredRelation('book', condition=Q(book__title__iexact='poem by alice')),
            ).filter(book_alice__isnull=False).select_related('book_alice').only('book_alice__state')

    def test_as_subquery(self):
        """
        Tests filtering authors based on a subquery that filters books with a specific title.
        
        Key Parameters:
        - None
        
        Key Keyword Arguments:
        - None
        
        Returns:
        - None
        
        Explanation:
        This function tests the filtering of authors based on a subquery. The inner query annotates each author with a boolean indicating whether they have a book titled 'poem by alice'. The outer query filters authors who have such a book. The test asserts that the resulting queryset contains only the author1.
        """

        inner_qs = Author.objects.annotate(
            book_alice=FilteredRelation('book', condition=Q(book__title__iexact='poem by alice')),
        ).filter(book_alice__isnull=False)
        qs = Author.objects.filter(id__in=inner_qs)
        self.assertSequenceEqual(qs, [self.author1])

    def test_with_foreign_key_error(self):
        """
        Tests the behavior of the FilteredRelation method when used with a nested foreign key relationship.
        
        This function checks if an error is raised when attempting to use a nested foreign key relationship within the condition of a FilteredRelation. Specifically, it tries to filter based on a condition involving 'author__favorite_books__author'. If the condition is not supported, a ValueError should be raised with a specific message.
        
        Parameters:
        - self: The test case instance.
        
        Returns:
        - None: The function asserts that a
        """

        msg = (
            "FilteredRelation's condition doesn't support nested relations "
            "(got 'author__favorite_books__author')."
        )
        with self.assertRaisesMessage(ValueError, msg):
            list(Book.objects.annotate(
                alice_favorite_books=FilteredRelation(
                    'author__favorite_books',
                    condition=Q(author__favorite_books__author=self.author1),
                )
            ))

    def test_with_foreign_key_on_condition_error(self):
        msg = (
            "FilteredRelation's condition doesn't support nested relations "
            "(got 'book__editor__name__icontains')."
        )
        with self.assertRaisesMessage(ValueError, msg):
            list(Author.objects.annotate(
                book_edited_by_b=FilteredRelation('book', condition=Q(book__editor__name__icontains='b')),
            ))

    def test_with_empty_relation_name_error(self):
        with self.assertRaisesMessage(ValueError, 'relation_name cannot be empty.'):
            FilteredRelation('', condition=Q(blank=''))

    def test_with_condition_as_expression_error(self):
        msg = 'condition argument must be a Q() instance.'
        expression = Case(
            When(book__title__iexact='poem by alice', then=True), default=False,
        )
        with self.assertRaisesMessage(ValueError, msg):
            FilteredRelation('book', condition=expression)

    def test_with_prefetch_related(self):
        """
        Tests for the `prefetch_related` method with `FilteredRelation`.
        
        This function verifies that the `prefetch_related` method raises a ValueError when used in conjunction with a `FilteredRelation` query.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If `prefetch_related` is called on a queryset that contains a `FilteredRelation` query.
        
        Key Points:
        - The function creates a queryset that uses `annotate` with a `FilteredRelation` to filter books with titles
        """

        msg = 'prefetch_related() is not supported with FilteredRelation.'
        qs = Author.objects.annotate(
            book_title_contains_b=FilteredRelation('book', condition=Q(book__title__icontains='b')),
        ).filter(
            book_title_contains_b__isnull=False,
        )
        with self.assertRaisesMessage(ValueError, msg):
            qs.prefetch_related('book_title_contains_b')
        with self.assertRaisesMessage(ValueError, msg):
            qs.prefetch_related('book_title_contains_b__editor')

    def test_with_generic_foreign_key(self):
        """
        Tests filtering and annotating a queryset with a generic foreign key.
        
        This function tests the filtering and annotating of a queryset for a book model that has a generic foreign key relationship. It uses the `FilteredRelation` to conditionally include the related generic author only if it is not null.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Concepts:
        - `FilteredRelation`: A method used to conditionally include a related model in the queryset.
        - `Q`: A query object used to filter
        """

        self.assertSequenceEqual(
            Book.objects.annotate(
                generic_authored_book=FilteredRelation(
                    'generic_author',
                    condition=Q(generic_author__isnull=False)
                ),
            ).filter(generic_authored_book__isnull=False),
            [self.book1]
        )

    def test_eq(self):
        self.assertEqual(FilteredRelation('book', condition=Q(book__title='b')), mock.ANY)


class FilteredRelationAggregationTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author1 = Author.objects.create(name='Alice')
        cls.editor_a = Editor.objects.create(name='a')
        cls.book1 = Book.objects.create(
            title='Poem by Alice',
            editor=cls.editor_a,
            author=cls.author1,
        )
        cls.borrower1 = Borrower.objects.create(name='Jenny')
        cls.borrower2 = Borrower.objects.create(name='Kevin')
        # borrower 1 reserves, rents, and returns book1.
        Reservation.objects.create(
            borrower=cls.borrower1,
            book=cls.book1,
            state=Reservation.STOPPED,
        )
        RentalSession.objects.create(
            borrower=cls.borrower1,
            book=cls.book1,
            state=RentalSession.STOPPED,
        )
        # borrower2 reserves, rents, and returns book1.
        Reservation.objects.create(
            borrower=cls.borrower2,
            book=cls.book1,
            state=Reservation.STOPPED,
        )
        RentalSession.objects.create(
            borrower=cls.borrower2,
            book=cls.book1,
            state=RentalSession.STOPPED,
        )

    def test_aggregate(self):
        """
        filtered_relation() not only improves performance but also creates
        correct results when aggregating with multiple LEFT JOINs.

        Books can be reserved then rented by a borrower. Each reservation and
        rental session are recorded with Reservation and RentalSession models.
        Every time a reservation or a rental session is over, their state is
        changed to 'stopped'.

        Goal: Count number of books that are either currently reserved or
        rented by borrower1 or available.
        """
        qs = Book.objects.annotate(
            is_reserved_or_rented_by=Case(
                When(reservation__state=Reservation.NEW, then=F('reservation__borrower__pk')),
                When(rental_session__state=RentalSession.NEW, then=F('rental_session__borrower__pk')),
                default=None,
            )
        ).filter(
            Q(is_reserved_or_rented_by=self.borrower1.pk) | Q(state=Book.AVAILABLE)
        ).distinct()
        self.assertEqual(qs.count(), 1)
        # If count is equal to 1, the same aggregation should return in the
        # same result but it returns 4.
        self.assertSequenceEqual(qs.annotate(total=Count('pk')).values('total'), [{'total': 4}])
        # With FilteredRelation, the result is as expected (1).
        qs = Book.objects.annotate(
            active_reservations=FilteredRelation(
                'reservation', condition=Q(
                    reservation__state=Reservation.NEW,
                    reservation__borrower=self.borrower1,
                )
            ),
        ).annotate(
            active_rental_sessions=FilteredRelation(
                'rental_session', condition=Q(
                    rental_session__state=RentalSession.NEW,
                    rental_session__borrower=self.borrower1,
                )
            ),
        ).filter(
            (Q(active_reservations__isnull=False) | Q(active_rental_sessions__isnull=False)) |
            Q(state=Book.AVAILABLE)
        ).distinct()
        self.assertEqual(qs.count(), 1)
        self.assertSequenceEqual(qs.annotate(total=Count('pk')).values('total'), [{'total': 1}])
