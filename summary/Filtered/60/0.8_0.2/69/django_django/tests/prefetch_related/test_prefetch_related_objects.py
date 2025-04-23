from django.db.models import Prefetch, prefetch_related_objects
from django.test import TestCase

from .models import Author, Book, Reader


class PrefetchRelatedObjectsTests(TestCase):
    """
    Since prefetch_related_objects() is just the inner part of
    prefetch_related(), only do basic tests to ensure its API hasn't changed.
    """
    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls):
        A class method that sets up test data for the test cases.
        
        Parameters:
        cls (cls): The class object for which the test data is being set up.
        
        Returns:
        None
        
        Key Data Points:
        - Creates four Book objects with titles 'Poems', 'Jane Eyre', 'Wuthering Heights', and 'Sense and Sensibility'.
        - Creates four Author objects named 'Charlotte', 'Anne', 'Emily', and 'Jane'.
        -
        """

        cls.book1 = Book.objects.create(title='Poems')
        cls.book2 = Book.objects.create(title='Jane Eyre')
        cls.book3 = Book.objects.create(title='Wuthering Heights')
        cls.book4 = Book.objects.create(title='Sense and Sensibility')

        cls.author1 = Author.objects.create(name='Charlotte', first_book=cls.book1)
        cls.author2 = Author.objects.create(name='Anne', first_book=cls.book1)
        cls.author3 = Author.objects.create(name='Emily', first_book=cls.book1)
        cls.author4 = Author.objects.create(name='Jane', first_book=cls.book4)

        cls.book1.authors.add(cls.author1, cls.author2, cls.author3)
        cls.book2.authors.add(cls.author1)
        cls.book3.authors.add(cls.author3)
        cls.book4.authors.add(cls.author4)

        cls.reader1 = Reader.objects.create(name='Amy')
        cls.reader2 = Reader.objects.create(name='Belinda')

        cls.reader1.books_read.add(cls.book1, cls.book4)
        cls.reader2.books_read.add(cls.book2, cls.book4)

    def test_unknown(self):
        """
        Tests the behavior of prefetch_related_objects when an unknown attribute is specified.
        
        This function retrieves a book object from the database and attempts to use prefetch_related_objects with an unknown attribute. It expects an AttributeError to be raised due to the unknown attribute.
        
        Parameters:
        self (unittest.TestCase): The test case instance.
        
        Returns:
        None: This function does not return any value. It asserts that an AttributeError is raised.
        """

        book1 = Book.objects.get(id=self.book1.id)
        with self.assertRaises(AttributeError):
            prefetch_related_objects([book1], 'unknown_attribute')

    def test_m2m_forward(self):
        book1 = Book.objects.get(id=self.book1.id)
        with self.assertNumQueries(1):
            prefetch_related_objects([book1], 'authors')

        with self.assertNumQueries(0):
            self.assertCountEqual(book1.authors.all(), [self.author1, self.author2, self.author3])

    def test_m2m_reverse(self):
        author1 = Author.objects.get(id=self.author1.id)
        with self.assertNumQueries(1):
            prefetch_related_objects([author1], 'books')

        with self.assertNumQueries(0):
            self.assertCountEqual(author1.books.all(), [self.book1, self.book2])

    def test_foreignkey_forward(self):
        authors = list(Author.objects.all())
        with self.assertNumQueries(1):
            prefetch_related_objects(authors, 'first_book')

        with self.assertNumQueries(0):
            [author.first_book for author in authors]

    def test_foreignkey_reverse(self):
        books = list(Book.objects.all())
        with self.assertNumQueries(1):
            prefetch_related_objects(books, 'first_time_authors')

        with self.assertNumQueries(0):
            [list(book.first_time_authors.all()) for book in books]

    def test_m2m_then_m2m(self):
        """A m2m can be followed through another m2m."""
        authors = list(Author.objects.all())
        with self.assertNumQueries(2):
            prefetch_related_objects(authors, 'books__read_by')

        with self.assertNumQueries(0):
            self.assertEqual(
                [
                    [[str(r) for r in b.read_by.all()] for b in a.books.all()]
                    for a in authors
                ],
                [
                    [['Amy'], ['Belinda']],  # Charlotte - Poems, Jane Eyre
                    [['Amy']],               # Anne - Poems
                    [['Amy'], []],           # Emily - Poems, Wuthering Heights
                    [['Amy', 'Belinda']],    # Jane - Sense and Sense
                ]
            )

    def test_prefetch_object(self):
        book1 = Book.objects.get(id=self.book1.id)
        with self.assertNumQueries(1):
            prefetch_related_objects([book1], Prefetch('authors'))

        with self.assertNumQueries(0):
            self.assertCountEqual(book1.authors.all(), [self.author1, self.author2, self.author3])

    def test_prefetch_object_twice(self):
        """
        Tests prefetching of related objects for a single book and multiple books.
        
        This function tests the prefetching behavior of related objects for a single book and multiple books. It ensures that prefetching a single book and then prefetching multiple books with the same prefetch query do not result in additional database queries.
        
        Parameters:
        self (unittest.TestCase): The test case instance.
        
        Returns:
        None: This function does not return any value. It asserts the expected behavior of prefetching related objects.
        
        Key Points:
        -
        """

        book1 = Book.objects.get(id=self.book1.id)
        book2 = Book.objects.get(id=self.book2.id)
        with self.assertNumQueries(1):
            prefetch_related_objects([book1], Prefetch('authors'))
        with self.assertNumQueries(1):
            prefetch_related_objects([book1, book2], Prefetch('authors'))
        with self.assertNumQueries(0):
            self.assertCountEqual(book2.authors.all(), [self.author1])

    def test_prefetch_object_to_attr(self):
        book1 = Book.objects.get(id=self.book1.id)
        with self.assertNumQueries(1):
            prefetch_related_objects([book1], Prefetch('authors', to_attr='the_authors'))

        with self.assertNumQueries(0):
            self.assertCountEqual(book1.the_authors, [self.author1, self.author2, self.author3])

    def test_prefetch_object_to_attr_twice(self):
        book1 = Book.objects.get(id=self.book1.id)
        book2 = Book.objects.get(id=self.book2.id)
        with self.assertNumQueries(1):
            prefetch_related_objects(
                [book1],
                Prefetch('authors', to_attr='the_authors'),
            )
        with self.assertNumQueries(1):
            prefetch_related_objects(
                [book1, book2],
                Prefetch('authors', to_attr='the_authors'),
            )
        with self.assertNumQueries(0):
            self.assertCountEqual(book2.the_authors, [self.author1])

    def test_prefetch_queryset(self):
        """
        Tests the prefetch_queryset functionality.
        
        This function checks whether prefetching related objects using `prefetch_related_objects` works correctly. It performs a test by:
        1. Retrieving a book instance from the database.
        2. Prefetching the authors related to the book using a specific queryset that filters authors by their IDs.
        3. Verifying that the prefetching operation reduces the number of database queries to zero when accessing the prefetched data.
        
        Parameters:
        None
        
        Keywords:
        None
        
        Returns:
        """

        book1 = Book.objects.get(id=self.book1.id)
        with self.assertNumQueries(1):
            prefetch_related_objects(
                [book1],
                Prefetch('authors', queryset=Author.objects.filter(id__in=[self.author1.id, self.author2.id]))
            )

        with self.assertNumQueries(0):
            self.assertCountEqual(book1.authors.all(), [self.author1, self.author2])
