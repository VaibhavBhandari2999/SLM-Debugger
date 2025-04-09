from unittest import mock

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import connections
from django.test import TestCase, override_settings
from django.urls import path, reverse

from .models import Book


class Router:
    target_db = None

    def db_for_read(self, model, **hints):
        return self.target_db

    db_for_write = db_for_read


site = admin.AdminSite(name='test_adminsite')
site.register(Book)

urlpatterns = [
    path('admin/', site.urls),
]


@override_settings(ROOT_URLCONF=__name__, DATABASE_ROUTERS=['%s.Router' % __name__])
class MultiDatabaseTests(TestCase):
    databases = {'default', 'other'}

    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for multiple databases.
        
        This method creates superusers and test books for each database connection available. It uses the `User` model to create a superuser with the specified username, password, and email. For each database, it also creates a `Book` instance and saves it, storing the ID of the saved book in a dictionary.
        
        :param cls: The class object (typically a test case class) that this method is bound to.
        :type cls: class
        """

        cls.superusers = {}
        cls.test_book_ids = {}
        for db in connections:
            Router.target_db = db
            cls.superusers[db] = User.objects.create_superuser(
                username='admin', password='something', email='test@test.org',
            )
            b = Book(name='Test Book')
            b.save(using=db)
            cls.test_book_ids[db] = b.id

    @mock.patch('django.contrib.admin.options.transaction')
    def test_add_view(self, mock):
        """
        Tests the add view functionality for the Book model in the admin site. For each database connection, logs in a superuser, posts a new book with a specific name, and asserts that the atomic context manager is called with the correct database using the `mock` object.
        
        :param mock: A mock object used to verify the calls to the atomic context manager.
        """

        for db in connections:
            with self.subTest(db=db):
                Router.target_db = db
                self.client.force_login(self.superusers[db])
                self.client.post(
                    reverse('test_adminsite:admin_views_book_add'),
                    {'name': 'Foobar: 5th edition'},
                )
                mock.atomic.assert_called_with(using=db)

    @mock.patch('django.contrib.admin.options.transaction')
    def test_change_view(self, mock):
        """
        Tests the change view functionality for a book model in the admin site. For each database connection, logs in a superuser, changes the name of a book, and ensures that the transaction is managed using the specified database.
        
        Args:
        mock (unittest.mock.Mock): A mock object to verify the behavior of the atomic context manager.
        
        Summary:
        - Iterates over all database connections.
        - Uses `subTest` to handle each database separately.
        - Sets the target database for the
        """

        for db in connections:
            with self.subTest(db=db):
                Router.target_db = db
                self.client.force_login(self.superusers[db])
                self.client.post(
                    reverse('test_adminsite:admin_views_book_change', args=[self.test_book_ids[db]]),
                    {'name': 'Test Book 2: Test more'},
                )
                mock.atomic.assert_called_with(using=db)

    @mock.patch('django.contrib.admin.options.transaction')
    def test_delete_view(self, mock):
        """
        Tests the delete view functionality for different databases.
        
        This function iterates over each database connection, sets the target database,
        forces a superuser login, and posts a deletion request to the book delete view.
        It uses the `atomic` context manager from the `transaction` module to ensure
        database transactions are properly managed during the deletion process.
        
        Args:
        mock (unittest.mock.Mock): A mock object to track method calls.
        
        Summary:
        - Iterates over database connections.
        """

        for db in connections:
            with self.subTest(db=db):
                Router.target_db = db
                self.client.force_login(self.superusers[db])
                self.client.post(
                    reverse('test_adminsite:admin_views_book_delete', args=[self.test_book_ids[db]]),
                    {'post': 'yes'},
                )
                mock.atomic.assert_called_with(using=db)
