from django.core.exceptions import FieldError
from django.test import TestCase

from .models.default_related_name import Author, Book, Editor


class DefaultRelatedNameTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        ---------------------------------------------------------------------------
        Sets up test data for the class.
        
        Parameters:
        cls (cls): The test class object.
        
        Returns:
        None
        
        This method creates and initializes test data for use in unit tests. It creates an instance of the Author model, an instance of the Editor model, and an instance of the Book model, and then associates the author with the book.
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
        Tests the behavior of attempting to use a non-existent field in a model queryset lookup.
        
        This function asserts that a FieldError is raised when trying to use a non-existent field ('book') in a queryset lookup on the Author model.
        
        Parameters:
        self (TestInstance): The test instance used for assertions.
        
        Returns:
        None: This function does not return any value. It raises an exception if the test fails.
        
        Raises:
        FieldError: If the lookup is successful, indicating that the non-existent
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
