from unittest import mock

from django.db import connection, transaction
from django.db.models import Case, Count, F, FilteredRelation, Q, When
from django.test import TestCase
from django.test.testcases import skipUnlessDBFeature

from .models import Author, Book, Borrower, Editor, RentalSession, Reservation


class FilteredRelationTests(TestCase):

    @classmethod
    def setUpTestData(cls):
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
        """
        Tests the functionality of the `select_related` method in combination with `annotate` and `FilteredRelation`.
        
        This method creates a queryset of authors and their associated books and editors, using `annotate` to add a `FilteredRelation` of the book, and then `select_related` to pre-fetch the editor of the book. The resulting queryset is ordered by author and book join primary key.
        
        Parameters:
        - No external parameters are needed for this method.
        
        Returns:
        - A queryset of authors, their books
        """

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
        Tests the functionality of the `select_related` method in combination with `FilteredRelation`.
        
        This function creates a queryset of `Book` objects, annotates each with filtered relations for `author` and `editor`, and then selects related objects for these annotations. The resulting queryset is ordered by primary key.
        
        Key Parameters:
        - None
        
        Returns:
        - A queryset of `Book` objects, each with related `author` and `editor` objects.
        
        Expected Output:
        - A list of tuples, each containing
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
        """
        Tests the behavior of `select_related` with an empty relation.
        
        This function tests how Django's `select_related` works when used with an empty relation created using `FilteredRelation`. It creates a queryset of `Author` objects, annotates each with an empty 'book' relation, and then applies `select_related` to the annotated relation. The resulting queryset is then ordered by the primary key and compared to the expected output.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        -
        """

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
        Tests the behavior of `select_related` and `select_for_update` methods when used together with a `FilteredRelation` on a ForeignKey field.
        
        This test ensures that when querying a queryset with `select_related` and `select_for_update`, the related objects (in this case, the author) are properly fetched and locked for updates within a transaction.
        
        Key Parameters:
        - `self`: The test case instance.
        
        Key Methods:
        - `assertNumQueries`: Asserts the number of database queries executed.
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
        """
        Tests the `annotate` method with `FilteredRelation` to filter related objects based on a condition.
        
        Args:
        self: The test case instance.
        
        Returns:
        None
        
        Key Parameters:
        - `Author.objects.annotate(book_alice=FilteredRelation('book', condition=Q(book__title__iexact='poem by alice')))`:
        Annotates the `Author` queryset with a filtered relation named `book_alice` that includes only the books with the title 'poem
        """

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
        
        This function asserts that the query returns a sequence containing only the author1 object. The query filters authors who have either a book titled 'poem by alice' (case-insensitive) or a book with a state of 'RENTED'. The `FilteredRelation` is used to include only the relevant book information in the result.
        
        Parameters:
        - None (the function relies on internal Django ORM methods and objects)
        
        Returns:
        - None (the
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
        """
        Tests the filtering and annotation of authors based on books containing the term 'alice' in the title.
        
        This function performs the following operations:
        1. Annotates each author with a filtered relation to their books where the book title contains 'alice'.
        2. Filters the authors to include only those who have at least one book with 'alice' in the title.
        3. Ensures the results are distinct to avoid duplicates.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        The function asserts
        """

        self.assertSequenceEqual(
            Author.objects.annotate(
                book_title_alice=FilteredRelation('book', condition=Q(book__title__icontains='alice')),
            ).filter(book_title_alice__isnull=False).filter(book_title_alice__isnull=False).distinct(),
            [self.author1]
        )

    def test_exclude_relation_with_join(self):
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
        Tests filtering and joining multiple-to-many relationships with a filtered relation.
        
        This function filters and joins multiple-to-many relationships using a `FilteredRelation` to narrow down the query based on specific conditions. The `favorite_books_written_by_jane` annotated field is used to filter authors who have favorite books written by a specific author (`self.author2`) and edited by someone named 'b'. The result is distinct and ordered.
        
        Parameters:
        - `self.author2`: An instance of the `Author` model representing
        """

        qs = Author.objects.annotate(
            favorite_books_written_by_jane=FilteredRelation(
                'favorite_books', condition=Q(favorite_books__author=self.author2),
            )
        ).filter(favorite_books_written_by_jane__editor__name='b').distinct()
        self.assertSequenceEqual(qs, [self.author1])

    def test_values_list(self):
        """
        Tests the filtering and annotation of a queryset of Author objects based on the title of their books.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Steps:
        1. Annotates each Author object with a filtered relation named 'book_alice', which includes only books with the title 'Poem by Alice'.
        2. Filters the annotated Author objects to include only those that have a non-null 'book_alice' relation.
        3. Extracts the titles of the filtered books as a list
        """

        self.assertSequenceEqual(
            Author.objects.annotate(
                book_alice=FilteredRelation('book', condition=Q(book__title__iexact='poem by alice')),
            ).filter(book_alice__isnull=False).values_list('book_alice__title', flat=True),
            ['Poem by Alice']
        )

    def test_values(self):
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
        
        This function tests the intersection of two query sets (qs1 and qs2) to ensure they do not have any common elements.
        
        Parameters:
        - self: The current instance of the class.
        
        Key Parameters:
        - qs1: A Django QuerySet that is annotated with a FilteredRelation for books titled 'poem by alice' and filtered to include only those authors who have such a book.
        - qs2: A Django QuerySet that is annotated with a Filtered
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
        inner_qs = Author.objects.annotate(
            book_alice=FilteredRelation('book', condition=Q(book__title__iexact='poem by alice')),
        ).filter(book_alice__isnull=False)
        qs = Author.objects.filter(id__in=inner_qs)
        self.assertSequenceEqual(qs, [self.author1])

    def test_with_foreign_key_error(self):
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
=Count('pk')).values('total'), [{'total': 1}])
