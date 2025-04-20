from django.core.exceptions import FieldError
from django.test import TestCase

from .models.default_related_name import Author, Book, Editor


class DefaultRelatedNameTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        
        A class method that sets up test data for the class. This method is used to create a set of reusable test data that can be shared among multiple test methods.
        
        Parameters:
        cls: The test class itself. This is a reference to the class where the method is defined.
        
        Returns:
        None: This method does not return any value. It populates the database with test data.
        
        Key Data Points:
        - Creates an instance of the
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
        Tests that a specific model name is not available in a queryset lookup.
        
        This function checks if the model name 'book' is not available in a queryset lookup for the 'Author' model. If the model name is available, a FieldError is expected to be raised with a specific error message.
        
        Parameters:
        self (unittest.TestCase): The test case instance.
        
        Raises:
        FieldError: If the model name 'book' is available in the queryset lookup, this error is raised with the message "
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
