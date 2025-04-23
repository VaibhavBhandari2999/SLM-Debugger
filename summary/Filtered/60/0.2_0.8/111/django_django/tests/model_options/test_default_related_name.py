from django.core.exceptions import FieldError
from django.test import TestCase

from .models.default_related_name import Author, Book, Editor


class DefaultRelatedNameTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the Book model and related entities.
        
        This method creates and populates instances of the Author, Editor, and Book models for testing purposes. It is a class method that should be used to initialize test data before running tests.
        
        Key Parameters:
        - cls: The test class instance.
        
        Returns:
        - None: This method does not return any value. It populates the database with test data.
        
        Example Usage:
        ```python
        class BookTest(TestCase):
        @classmethod
        def setUp
        """

        cls.author = Author.objects.create(first_name="Dave", last_name="Loper")
        cls.editor = Editor.objects.create(
            name="Test Editions", bestselling_author=cls.author
        )
        cls.book = Book.objects.create(title="Test Book", editor=cls.editor)
        cls.book.authors.add(cls.author)

    def test_no_default_related_name(self):
        self.assertEqual(list(self.author.editor_set.all()), [self.editor])

    def test_default_related_name(self):
        self.assertEqual(list(self.author.books.all()), [self.book])

    def test_default_related_name_in_queryset_lookup(self):
        self.assertEqual(Author.objects.get(books=self.book), self.author)

    def test_model_name_not_available_in_queryset_lookup(self):
        """
        Tests the behavior of a model query when an unavailable field is used.
        
        This function checks if attempting to query an Author model using an unavailable field 'book' raises a FieldError with the expected message.
        
        Parameters:
        self (object): The test case instance.
        
        Returns:
        None: This function does not return any value. It asserts that a FieldError is raised with the correct message.
        """

        msg = "Cannot resolve keyword 'book' into field."
        with self.assertRaisesMessage(FieldError, msg):
            Author.objects.get(book=self.book)

    def test_related_name_overrides_default_related_name(self):
        self.assertEqual(list(self.editor.edited_books.all()), [self.book])

    def test_inheritance(self):
        # model_options is the name of the application for this test.
        self.assertEqual(list(self.book.model_options_bookstores.all()), [])

    def test_inheritance_with_overridden_default_related_name(self):
        self.assertEqual(list(self.book.editor_stores.all()), [])
