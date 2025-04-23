from importlib import import_module

from django.apps import apps
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.db import connection, connections
from django.test import TransactionTestCase
from django.test.utils import captured_stdout

from .models import Proxy, UserProxy

update_proxy_permissions = import_module('django.contrib.auth.migrations.0011_update_proxy_permissions')


class ProxyModelWithDifferentAppLabelTests(TransactionTestCase):
    available_apps = [
        'auth_tests',
        'django.contrib.auth',
        'django.contrib.contenttypes',
    ]

    def setUp(self):
        """
        Create proxy permissions with content_type to the concrete model
        rather than the proxy model (as they were before Django 2.2 and
        migration 11).
        """
        Permission.objects.all().delete()
        self.concrete_content_type = ContentType.objects.get_for_model(UserProxy)
        self.default_permission = Permission.objects.create(
            content_type=self.concrete_content_type,
            codename='add_userproxy',
            name='Can add userproxy',
        )
        self.custom_permission = Permission.objects.create(
            content_type=self.concrete_content_type,
            codename='use_different_app_label',
            name='May use a different app label',
        )

    def test_proxy_model_permissions_contenttype(self):
        """
        Function to test proxy model permissions and content type updates.
        
        This function checks the content type of default and custom permissions for a proxy model and updates the content type if necessary. It uses a database schema editor to perform the update.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Retrieves the content type for the proxy model (UserProxy) that is not concrete.
        2. Compares the content types of default and custom permissions with the concrete content type.
        3. Uses a database
        """

        proxy_model_content_type = ContentType.objects.get_for_model(UserProxy, for_concrete_model=False)
        self.assertEqual(self.default_permission.content_type, self.concrete_content_type)
        self.assertEqual(self.custom_permission.content_type, self.concrete_content_type)
        with connection.schema_editor() as editor:
            update_proxy_permissions.update_proxy_model_permissions(apps, editor)
        self.default_permission.refresh_from_db()
        self.assertEqual(self.default_permission.content_type, proxy_model_content_type)
        self.custom_permission.refresh_from_db()
        self.assertEqual(self.custom_permission.content_type, proxy_model_content_type)

    def test_user_has_now_proxy_model_permissions(self):
        user = User.objects.create()
        user.user_permissions.add(self.default_permission)
        user.user_permissions.add(self.custom_permission)
        for permission in [self.default_permission, self.custom_permission]:
            self.assertTrue(user.has_perm('auth.' + permission.codename))
            self.assertFalse(user.has_perm('auth_tests.' + permission.codename))
        with connection.schema_editor() as editor:
            update_proxy_permissions.update_proxy_model_permissions(apps, editor)
        # Reload user to purge the _perm_cache.
        user = User._default_manager.get(pk=user.pk)
        for permission in [self.default_permission, self.custom_permission]:
            self.assertFalse(user.has_perm('auth.' + permission.codename))
            self.assertTrue(user.has_perm('auth_tests.' + permission.codename))

    def test_migrate_backwards(self):
        with connection.schema_editor() as editor:
            update_proxy_permissions.update_proxy_model_permissions(apps, editor)
            update_proxy_permissions.revert_proxy_model_permissions(apps, editor)
        self.default_permission.refresh_from_db()
        self.assertEqual(self.default_permission.content_type, self.concrete_content_type)
        self.custom_permission.refresh_from_db()
        self.assertEqual(self.custom_permission.content_type, self.concrete_content_type)

    def test_user_keeps_same_permissions_after_migrating_backward(self):
        user = User.objects.create()
        user.user_permissions.add(self.default_permission)
        user.user_permissions.add(self.custom_permission)
        for permission in [self.default_permission, self.custom_permission]:
            self.assertTrue(user.has_perm('auth.' + permission.codename))
            self.assertFalse(user.has_perm('auth_tests.' + permission.codename))
        with connection.schema_editor() as editor:
            update_proxy_permissions.update_proxy_model_permissions(apps, editor)
            update_proxy_permissions.revert_proxy_model_permissions(apps, editor)
        # Reload user to purge the _perm_cache.
        user = User._default_manager.get(pk=user.pk)
        for permission in [self.default_permission, self.custom_permission]:
            self.assertTrue(user.has_perm('auth.' + permission.codename))
            self.assertFalse(user.has_perm('auth_tests.' + permission.codename))


class ProxyModelWithSameAppLabelTests(TransactionTestCase):
    available_apps = [
        'auth_tests',
        'django.contrib.auth',
        'django.contrib.contenttypes',
    ]

    def setUp(self):
        """
        Create proxy permissions with content_type to the concrete model
        rather than the proxy model (as they were before Django 2.2 and
        migration 11).
        """
        Permission.objects.all().delete()
        self.concrete_content_type = ContentType.objects.get_for_model(Proxy)
        self.default_permission = Permission.objects.create(
            content_type=self.concrete_content_type,
            codename='add_proxy',
            name='Can add proxy',
        )
        self.custom_permission = Permission.objects.create(
            content_type=self.concrete_content_type,
            codename='display_proxys',
            name='May display proxys information',
        )

    def test_proxy_model_permissions_contenttype(self):
        """
        Tests the behavior of updating permissions for a proxy model.
        
        This function checks the content type of default and custom permissions before and after updating the proxy model permissions. It ensures that the content type is correctly updated to the proxy model's content type after the update.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Retrieves the content type for the proxy model, ensuring it is for a non-concrete model.
        2. Compares the initial content types of the default and custom permissions with
        """

        proxy_model_content_type = ContentType.objects.get_for_model(Proxy, for_concrete_model=False)
        self.assertEqual(self.default_permission.content_type, self.concrete_content_type)
        self.assertEqual(self.custom_permission.content_type, self.concrete_content_type)
        with connection.schema_editor() as editor:
            update_proxy_permissions.update_proxy_model_permissions(apps, editor)
        self.default_permission.refresh_from_db()
        self.custom_permission.refresh_from_db()
        self.assertEqual(self.default_permission.content_type, proxy_model_content_type)
        self.assertEqual(self.custom_permission.content_type, proxy_model_content_type)

    def test_user_still_has_proxy_model_permissions(self):
        user = User.objects.create()
        user.user_permissions.add(self.default_permission)
        user.user_permissions.add(self.custom_permission)
        for permission in [self.default_permission, self.custom_permission]:
            self.assertTrue(user.has_perm('auth_tests.' + permission.codename))
        with connection.schema_editor() as editor:
            update_proxy_permissions.update_proxy_model_permissions(apps, editor)
        # Reload user to purge the _perm_cache.
        user = User._default_manager.get(pk=user.pk)
        for permission in [self.default_permission, self.custom_permission]:
            self.assertTrue(user.has_perm('auth_tests.' + permission.codename))

    def test_migrate_backwards(self):
        """
        Tests the migration of permissions for proxy models.
        
        This function checks the migration of permissions for proxy models. It uses a schema editor to update and revert the proxy model permissions. After the operations, it refreshes the default and custom permissions from the database and asserts that their content types have been correctly updated to the concrete content type.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Uses a schema editor to update the proxy model permissions.
        2. Reverts the proxy model permissions.
        """

        with connection.schema_editor() as editor:
            update_proxy_permissions.update_proxy_model_permissions(apps, editor)
            update_proxy_permissions.revert_proxy_model_permissions(apps, editor)
        self.default_permission.refresh_from_db()
        self.assertEqual(self.default_permission.content_type, self.concrete_content_type)
        self.custom_permission.refresh_from_db()
        self.assertEqual(self.custom_permission.content_type, self.concrete_content_type)

    def test_user_keeps_same_permissions_after_migrating_backward(self):
        user = User.objects.create()
        user.user_permissions.add(self.default_permission)
        user.user_permissions.add(self.custom_permission)
        for permission in [self.default_permission, self.custom_permission]:
            self.assertTrue(user.has_perm('auth_tests.' + permission.codename))
        with connection.schema_editor() as editor:
            update_proxy_permissions.update_proxy_model_permissions(apps, editor)
            update_proxy_permissions.revert_proxy_model_permissions(apps, editor)
        # Reload user to purge the _perm_cache.
        user = User._default_manager.get(pk=user.pk)
        for permission in [self.default_permission, self.custom_permission]:
            self.assertTrue(user.has_perm('auth_tests.' + permission.codename))

    def test_migrate_with_existing_target_permission(self):
        """
        Permissions may already exist:

        - Old workaround was to manually create permissions for proxy models.
        - Model may have been concrete and then converted to proxy.

        Output a reminder to audit relevant permissions.
        """
        proxy_model_content_type = ContentType.objects.get_for_model(Proxy, for_concrete_model=False)
        Permission.objects.create(
            content_type=proxy_model_content_type,
            codename='add_proxy',
            name='Can add proxy',
        )
        Permission.objects.create(
            content_type=proxy_model_content_type,
            codename='display_proxys',
            name='May display proxys information',
        )
        with captured_stdout() as stdout:
            with connection.schema_editor() as editor:
                update_proxy_permissions.update_proxy_model_permissions(apps, editor)
        self.assertIn('A problem arose migrating proxy model permissions', stdout.getvalue())


class MultiDBProxyModelAppLabelTests(TransactionTestCase):
    databases = {'default', 'other'}
    available_apps = [
        'auth_tests',
        'django.contrib.auth',
        'django.contrib.contenttypes',
    ]

    def setUp(self):
        """
        Sets up the test environment by deleting all content types and permissions in the 'other' database. It then creates a new permission for the Proxy model in the 'other' database.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Deletes all existing content types from the 'other' database.
        2. Deletes all existing permissions from the 'other' database.
        3. Retrieves the content type for the Proxy model using the 'other' database connection.
        4. Creates a new permission
        """

        ContentType.objects.all().delete()
        Permission.objects.using('other').delete()
        concrete_content_type = ContentType.objects.db_manager(
            'other'
        ).get_for_model(Proxy)
        self.permission = Permission.objects.using('other').create(
            content_type=concrete_content_type,
            codename='add_proxy',
            name='Can add proxy',
        )

    def test_migrate_other_database(self):
        proxy_model_content_type = ContentType.objects.db_manager(
            'other'
        ).get_for_model(Proxy, for_concrete_model=False)
        with connections['other'].schema_editor() as editor:
            update_proxy_permissions.update_proxy_model_permissions(apps, editor)
        self.permission.refresh_from_db()
        self.assertEqual(self.permission.content_type, proxy_model_content_type)
content_type, proxy_model_content_type)
