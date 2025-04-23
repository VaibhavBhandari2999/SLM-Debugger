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
        with self.assertRaisesMessage(RemovedInDjango51Warning, self.msg):
            with self.settings(
                STATICFILES_STORAGE=(
                    "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
                )
            ):
                pass

    def test_settings_init(self):
        """
        Tests the initialization of the Settings class with a custom settings module.
        
        This function creates a mock settings module and sets specific attributes to test the behavior of the Settings class. It raises a RemovedInDjango51Warning if the settings module contains certain attributes. The function ensures that the warning is raised and then cleans up by removing the mock module from sys.modules.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        RemovedInDjango51Warning: If the settings module contains attributes that
        """

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
        """
        Tests the access of the STATICFILES_STORAGE setting within a settings context.
        
        This function temporarily sets the STATICFILES_STORAGE setting to 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage' using the `settings` context manager. It then verifies that the setting is correctly set to the expected value. The test is repeated to ensure that the setting remains consistent after the context manager exits.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Inputs:
        - None
        
        Outputs:
        - None
        
        Side Effects:
        -
        """

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
        """
        Tests the behavior when both USE_TZ and STORAGES/STATICFILES_STORAGE are set in the settings.
        
        This function checks that an ImproperlyConfigured error is raised when both USE_TZ and either STORAGES or STATICFILES_STORAGE are set in the Django settings. It ensures that these settings are mutually exclusive.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - Raises an ImproperlyConfigured error with the message "STATICFILES_STORAGE
        """

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
        empty_storages = StorageHandler()
        with self.settings(DEFAULT_FILE_STORAGE="django.core.files.storage.Storage"):
            self.assertIsInstance(storages[DEFAULT_STORAGE_ALIAS], Storage)
            self.assertIsInstance(empty_storages[DEFAULT_STORAGE_ALIAS], Storage)
            self.assertIsInstance(default_storage, Storage)
torage, Storage)
