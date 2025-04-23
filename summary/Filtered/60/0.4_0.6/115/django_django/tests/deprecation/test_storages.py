import sys
from types import ModuleType

from django.conf import (
    DEFAULT_FILE_STORAGE_DEPRECATED_MSG,
    DEFAULT_STORAGE_ALIAS,
    STATICFILES_STORAGE_ALIAS,
    STATICFILES_STORAGE_DEPRECATED_MSG,
    Settings,
    settings,
)
from django.contrib.staticfiles.storage import (
    ManifestStaticFilesStorage,
    staticfiles_storage,
)
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import Storage, StorageHandler, default_storage, storages
from django.test import TestCase, ignore_warnings
from django.utils.deprecation import RemovedInDjango51Warning


class StaticfilesStorageDeprecationTests(TestCase):
    msg = STATICFILES_STORAGE_DEPRECATED_MSG

    def test_override_settings_warning(self):
        """
        Tests the override of settings to raise a RemovedInDjango51Warning.
        
        This function checks if overriding the STATICFILES_STORAGE setting with a specific storage class raises the expected warning.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        RemovedInDjango51Warning: If the override does not raise the expected warning.
        """

        with self.assertRaisesMessage(RemovedInDjango51Warning, self.msg):
            with self.settings(
                STATICFILES_STORAGE=(
                    "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
                )
            ):
                pass

    def test_settings_init(self):
        settings_module = ModuleType("fake_settings_module")
        settings_module.USE_TZ = True
        settings_module.STATICFILES_STORAGE = (
            "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
        )
        sys.modules["fake_settings_module"] = settings_module
        try:
            with self.assertRaisesMessage(RemovedInDjango51Warning, self.msg):
                Settings("fake_settings_module")
        finally:
            del sys.modules["fake_settings_module"]

    def test_access_warning(self):
        with self.assertRaisesMessage(RemovedInDjango51Warning, self.msg):
            settings.STATICFILES_STORAGE
        # Works a second time.
        with self.assertRaisesMessage(RemovedInDjango51Warning, self.msg):
            settings.STATICFILES_STORAGE

    @ignore_warnings(category=RemovedInDjango51Warning)
    def test_access(self):
        with self.settings(
            STATICFILES_STORAGE=(
                "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
            )
        ):
            self.assertEqual(
                settings.STATICFILES_STORAGE,
                "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
            )
            # Works a second time.
            self.assertEqual(
                settings.STATICFILES_STORAGE,
                "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
            )

    def test_use_both_error(self):
        msg = "STATICFILES_STORAGE/STORAGES are mutually exclusive."
        settings_module = ModuleType("fake_settings_module")
        settings_module.USE_TZ = True
        settings_module.STATICFILES_STORAGE = (
            "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
        )
        settings_module.STORAGES = {}
        sys.modules["fake_settings_module"] = settings_module
        try:
            with self.assertRaisesMessage(ImproperlyConfigured, msg):
                Settings("fake_settings_module")
        finally:
            del sys.modules["fake_settings_module"]

    @ignore_warnings(category=RemovedInDjango51Warning)
    def test_storage(self):
        """
        Tests the behavior of the `StorageHandler` class and the `STATICFILES_STORAGE` setting.
        
        This function checks the `StorageHandler` class and the `STATICFILES_STORAGE` setting to ensure that the correct storage classes are being used. It sets the `STATICFILES_STORAGE` to `ManifestStaticFilesStorage` and verifies that the storage instances are of the expected type.
        
        Key Parameters:
        - None
        
        Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - None
        
        Assertions:
        - `self
        """

        empty_storages = StorageHandler()
        with self.settings(
            STATICFILES_STORAGE=(
                "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
            )
        ):
            self.assertIsInstance(
                storages[STATICFILES_STORAGE_ALIAS],
                ManifestStaticFilesStorage,
            )
            self.assertIsInstance(
                empty_storages[STATICFILES_STORAGE_ALIAS],
                ManifestStaticFilesStorage,
            )
            self.assertIsInstance(staticfiles_storage, ManifestStaticFilesStorage)


class DefaultStorageDeprecationTests(TestCase):
    msg = DEFAULT_FILE_STORAGE_DEPRECATED_MSG

    def test_override_settings_warning(self):
        with self.assertRaisesMessage(RemovedInDjango51Warning, self.msg):
            with self.settings(
                DEFAULT_FILE_STORAGE=("django.core.files.storage.Storage")
            ):
                pass

    def test_settings_init(self):
        settings_module = ModuleType("fake_settings_module")
        settings_module.USE_TZ = True
        settings_module.DEFAULT_FILE_STORAGE = "django.core.files.storage.Storage"
        sys.modules["fake_settings_module"] = settings_module
        try:
            with self.assertRaisesMessage(RemovedInDjango51Warning, self.msg):
                Settings("fake_settings_module")
        finally:
            del sys.modules["fake_settings_module"]

    def test_access_warning(self):
        """
        Tests the access warning for the DEFAULT_FILE_STORAGE setting.
        
        This function checks if accessing the DEFAULT_FILE_STORAGE setting raises a RemovedInDjango51Warning. It tests this twice to ensure the warning is consistent.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        RemovedInDjango51Warning: If the DEFAULT_FILE_STORAGE setting is accessed, this warning is raised.
        
        Usage:
        This function is used to verify that the DEFAULT_FILE_STORAGE setting is properly deprecated and triggers the expected warning
        """

        with self.assertRaisesMessage(RemovedInDjango51Warning, self.msg):
            settings.DEFAULT_FILE_STORAGE
        # Works a second time.
        with self.assertRaisesMessage(RemovedInDjango51Warning, self.msg):
            settings.DEFAULT_FILE_STORAGE

    @ignore_warnings(category=RemovedInDjango51Warning)
    def test_access(self):
        with self.settings(DEFAULT_FILE_STORAGE="django.core.files.storage.Storage"):
            self.assertEqual(
                settings.DEFAULT_FILE_STORAGE,
                "django.core.files.storage.Storage",
            )
            # Works a second time.
            self.assertEqual(
                settings.DEFAULT_FILE_STORAGE,
                "django.core.files.storage.Storage",
            )

    def test_use_both_error(self):
        msg = "DEFAULT_FILE_STORAGE/STORAGES are mutually exclusive."
        settings_module = ModuleType("fake_settings_module")
        settings_module.USE_TZ = True
        settings_module.DEFAULT_FILE_STORAGE = "django.core.files.storage.Storage"
        settings_module.STORAGES = {}
        sys.modules["fake_settings_module"] = settings_module
        try:
            with self.assertRaisesMessage(ImproperlyConfigured, msg):
                Settings("fake_settings_module")
        finally:
            del sys.modules["fake_settings_module"]

    @ignore_warnings(category=RemovedInDjango51Warning)
    def test_storage(self):
        """
        Tests the functionality of the StorageHandler and the default file storage settings.
        
        This function checks the behavior of the StorageHandler and the default file storage settings in Django. It ensures that the default storage alias is correctly set and that the storage instances are of the expected type.
        
        Key Parameters:
        - None
        
        Returns:
        - None
        
        Steps:
        1. Initializes an empty StorageHandler instance.
        2. Sets the DEFAULT_FILE_STORAGE setting to "django.core.files.storage.Storage".
        3. Verifies that the storage instance for
        """

        empty_storages = StorageHandler()
        with self.settings(DEFAULT_FILE_STORAGE="django.core.files.storage.Storage"):
            self.assertIsInstance(storages[DEFAULT_STORAGE_ALIAS], Storage)
            self.assertIsInstance(empty_storages[DEFAULT_STORAGE_ALIAS], Storage)
            self.assertIsInstance(default_storage, Storage)
