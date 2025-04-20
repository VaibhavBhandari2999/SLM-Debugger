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
        setUpTestData(cls)
        Summary:
        Sets up test data for the test cases in the class. This method is called once before any test method in the class is run.
        
        Parameters:
        cls: The test class instance.
        
        Returns:
        None
        
        Description:
        This method creates and initializes several test objects, including books, authors, and readers. It is intended to be used for setting up a consistent dataset for multiple test cases within a test class. The data includes four books
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
        """
        Tests the reverse Many-to-Many relationship for an Author model.
        
        This function retrieves an Author instance and uses `prefetch_related_objects` to prefetch the related Books. It then asserts that no additional database queries are made when checking the Books related to the Author.
        
        Parameters:
        - None
        
        Keywords:
        - author1: The Author instance to test.
        - book1: The first Book instance related to `author1`.
        - book2: The second Book instance related to `author1`.
        
        Returns:
        -
        """

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
        Tests the prefetching behavior of Django's prefetch_related_objects function.
        
        This function checks how prefetching works when called multiple times on the same or different objects.
        
        Parameters:
        - book1 (Book): The first book object to be prefetched.
        - book2 (Book): The second book object to be prefetched.
        
        Key Points:
        - The function first retrieves two book objects from the database.
        - It then uses the `prefetch_related_objects` function to prefetch the 'authors' relationship for `book
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
        """
        Tests the prefetching of related objects to an attribute.
        
        This function retrieves a book object from the database and prefetches its authors to an attribute named 'the_authors'. It ensures that only one query is executed during the prefetch operation and no additional queries are made when accessing the 'the_authors' attribute.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - The number of database queries during the prefetch operation is exactly one.
        - The 'the_authors' attribute of the book object
        """

        book1 = Book.objects.get(id=self.book1.id)
        with self.assertNumQueries(1):
            prefetch_related_objects([book1], Prefetch('authors', to_attr='the_authors'))

        with self.assertNumQueries(0):
            self.assertCountEqual(book1.the_authors, [self.author1, self.author2, self.author3])

    def test_prefetch_object_to_attr_twice(self):
        """
        Tests the prefetching of related objects to an attribute using `prefetch_related_objects`.
        
        This function tests the behavior of prefetching related objects to an attribute using `prefetch_related_objects` method. It ensures that the prefetching is performed correctly even when the same prefetch operation is called multiple times with different sets of objects.
        
        Parameters:
        - None (The function uses pre-defined objects and assertions)
        
        Key Steps:
        1. Retrieves two book objects from the database.
        2. Prefetches the authors for the
        """

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
        book1 = Book.objects.get(id=self.book1.id)
        with self.assertNumQueries(1):
            prefetch_related_objects(
                [book1],
                Prefetch('authors', queryset=Author.objects.filter(id__in=[self.author1.id, self.author2.id]))
            )

        with self.assertNumQueries(0):
            self.assertCountEqual(book1.authors.all(), [self.author1, self.author2])
author2])
