from django.core.exceptions import FieldError
from django.test import TestCase

from .models.default_related_name import Author, Book, Editor


class DefaultRelatedNameTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the tests.
        
        This method creates and saves several test objects to the database:
        - An `Author` instance with first name 'Dave' and last name 'Loper'.
        - An `Editor` instance named 'Test Editions' with the created `Author` as the bestselling author.
        - A `Book` titled 'Test Book' with the created `Editor` as its editor.
        - Adds the `Author` to the `Book`'s authors.
        
        This method is
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
