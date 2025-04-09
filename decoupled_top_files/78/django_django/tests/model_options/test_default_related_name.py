"""
The provided Python file contains unit tests for Django models related to authors, editors, and books. It primarily focuses on testing the behavior of related names defined in the models. The file includes several test methods to ensure that:

1. The default related name works correctly.
2. Custom related names override the default ones.
3. Inheritance and overridden related names are handled properly.
4. Unavailable model names in queryset lookups raise appropriate exceptions.

The `DefaultRelatedNameTests` class inherits from `TestCase` and uses the `setUpTestData` method to create and set up test data. Each test method then performs assertions to validate the expected behavior of the related names in different scenarios. ```python
"""
from django.core.exceptions import FieldError
from django.test import TestCase

from .models.default_related_name import Author, Book, Editor


class DefaultRelatedNameTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the tests.
        
        This method creates instances of `Author`, `Editor`, and `Book` models and adds relationships between them. It is intended to be used as a class-level setup for testing purposes.
        
        Keyword arguments:
        None
        
        Returns:
        None
        
        Important functions and models used:
        - `Author.objects.create`: Creates an author instance with specified first and last names.
        - `Editor.objects.create`: Creates an editor instance with a specified name and
        """

        cls.author = Author.objects.create(first_name='Dave', last_name='Loper')
        cls.editor = Editor.objects.create(name='Test Editions', bestselling_author=cls.author)
        cls.book = Book.objects.create(title='Test Book', editor=cls.editor)
        cls.book.authors.add(cls.author)

    def test_no_default_related_name(self):
        self.assertEqual(list(self.author.editor_set.all()), [self.editor])

    def test_default_related_name(self):
        self.assertEqual(list(self.author.books.all()), [self.book])

    def test_default_related_name_in_queryset_lookup(self):
        self.assertEqual(Author.objects.get(books=self.book), self.author)

    def test_model_name_not_available_in_queryset_lookup(self):
        """
        Tests that attempting to use an unavailable model name ('book') in a queryset lookup raises a FieldError.
        
        Args:
        self: The current test case instance.
        
        Raises:
        FieldError: If the lookup is successful without raising an error.
        
        Important Functions:
        - `Author.objects.get()`: Attempts to retrieve an author object using the specified lookup.
        - `self.assertRaisesMessage()`: Asserts that a specific exception is raised with a given message.
        
        Keywords:
        - `
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
