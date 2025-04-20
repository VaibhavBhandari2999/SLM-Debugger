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
        
        This method initializes superusers and test books for each database connection. It creates a superuser with the username 'admin', password 'something', and email 'test@test.org'. Additionally, it creates a test book and stores its ID for each database.
        
        Parameters:
        cls (cls): The class object on which the method is called.
        
        Returns:
        None: This method does not return any value. It modifies the class attributes directly.
        
        Notes:
        - The
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
        Function to test the delete view functionality in the admin site.
        
        This function tests the delete view for a specific model (Book) in the admin site. It ensures that the deletion process is correctly handled for different database connections.
        
        Parameters:
        mock (unittest.mock.Mock): A mock object used to verify the behavior of the atomic context manager.
        
        Key Steps:
        1. Iterates over each database connection.
        2. Sets the target database for the router to the current database.
        3. Forces the login of a
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
