import pathlib

from django.core.checks import Warning
from django.core.checks.caches import (
    E001,
    check_cache_location_not_exposed,
    check_default_cache_is_configured,
    check_file_based_cache_is_absolute,
)
from django.test import SimpleTestCase
from django.test.utils import override_settings


class CheckCacheSettingsAppDirsTest(SimpleTestCase):
    VALID_CACHES_CONFIGURATION = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        },
    }
    INVALID_CACHES_CONFIGURATION = {
        "other": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        },
    }

    @override_settings(CACHES=VALID_CACHES_CONFIGURATION)
    def test_default_cache_included(self):
        """
        Don't error if 'default' is present in CACHES setting.
        """
        self.assertEqual(check_default_cache_is_configured(None), [])

    @override_settings(CACHES=INVALID_CACHES_CONFIGURATION)
    def test_default_cache_not_included(self):
        """
        Error if 'default' not present in CACHES setting.
        """
        self.assertEqual(check_default_cache_is_configured(None), [E001])


class CheckCacheLocationTest(SimpleTestCase):
    warning_message = (
        "Your 'default' cache configuration might expose your cache or lead "
        "to corruption of your data because its LOCATION %s %s."
    )

    @staticmethod
    def get_settings(setting, cache_path, setting_path):
        """
        Generate settings configuration for Django.
        
        This function creates a dictionary containing settings for Django, specifically for caching and static files.
        
        Parameters:
        setting (str): The setting key to configure, such as 'CACHES' or 'STATICFILES_DIRS'.
        cache_path (str): The path to the cache directory.
        setting_path (str): The path to the static files directory.
        
        Returns:
        dict: A dictionary containing the configured settings.
        
        Example:
        >>> get_settings('CACHES', '/
        """

        return {
            "CACHES": {
                "default": {
                    "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
                    "LOCATION": cache_path,
                },
            },
            setting: [setting_path] if setting == "STATICFILES_DIRS" else setting_path,
        }

    def test_cache_path_matches_media_static_setting(self):
        root = pathlib.Path.cwd()
        for setting in ("MEDIA_ROOT", "STATIC_ROOT", "STATICFILES_DIRS"):
            settings = self.get_settings(setting, root, root)
            with self.subTest(setting=setting), self.settings(**settings):
                msg = self.warning_message % ("matches", setting)
                self.assertEqual(
                    check_cache_location_not_exposed(None),
                    [
                        Warning(msg, id="caches.W002"),
                    ],
                )

    def test_cache_path_inside_media_static_setting(self):
        root = pathlib.Path.cwd()
        for setting in ("MEDIA_ROOT", "STATIC_ROOT", "STATICFILES_DIRS"):
            settings = self.get_settings(setting, root / "cache", root)
            with self.subTest(setting=setting), self.settings(**settings):
                msg = self.warning_message % ("is inside", setting)
                self.assertEqual(
                    check_cache_location_not_exposed(None),
                    [
                        Warning(msg, id="caches.W002"),
                    ],
                )

    def test_cache_path_contains_media_static_setting(self):
        """
        Tests the cache path to ensure it does not contain the MEDIA_ROOT, STATIC_ROOT, or STATICFILES_DIRS settings.
        
        This function iterates over the MEDIA_ROOT, STATIC_ROOT, and STATICFILES_DIRS settings to check if the cache path is contained within any of these settings. It uses the current working directory as the default root and an alternative root for comparison. The function generates a warning message if the cache path is found within any of the specified settings.
        
        Parameters:
        - setting (str): The setting to
        """

        root = pathlib.Path.cwd()
        for setting in ("MEDIA_ROOT", "STATIC_ROOT", "STATICFILES_DIRS"):
            settings = self.get_settings(setting, root, root / "other")
            with self.subTest(setting=setting), self.settings(**settings):
                msg = self.warning_message % ("contains", setting)
                self.assertEqual(
                    check_cache_location_not_exposed(None),
                    [
                        Warning(msg, id="caches.W002"),
                    ],
                )

    def test_cache_path_not_conflict(self):
        """
        Tests that the cache path does not conflict with other settings.
        
        This function checks that the cache path specified in the settings does not conflict with other paths such as MEDIA_ROOT, STATIC_ROOT, or STATICFILES_DIRS. It creates a temporary settings configuration for each of these settings, setting the cache path to a subdirectory of the current working directory and another path to ensure that the cache path is not exposed or conflicting.
        
        Parameters:
        None
        
        Returns:
        None
        
        Subtests:
        - MEDIA_ROOT:
        """

        root = pathlib.Path.cwd()
        for setting in ("MEDIA_ROOT", "STATIC_ROOT", "STATICFILES_DIRS"):
            settings = self.get_settings(setting, root / "cache", root / "other")
            with self.subTest(setting=setting), self.settings(**settings):
                self.assertEqual(check_cache_location_not_exposed(None), [])

    def test_staticfiles_dirs_prefix(self):
        root = pathlib.Path.cwd()
        tests = [
            (root, root, "matches"),
            (root / "cache", root, "is inside"),
            (root, root / "other", "contains"),
        ]
        for cache_path, setting_path, msg in tests:
            settings = self.get_settings(
                "STATICFILES_DIRS",
                cache_path,
                ("prefix", setting_path),
            )
            with self.subTest(path=setting_path), self.settings(**settings):
                msg = self.warning_message % (msg, "STATICFILES_DIRS")
                self.assertEqual(
                    check_cache_location_not_exposed(None),
                    [
                        Warning(msg, id="caches.W002"),
                    ],
                )

    def test_staticfiles_dirs_prefix_not_conflict(self):
        root = pathlib.Path.cwd()
        settings = self.get_settings(
            "STATICFILES_DIRS",
            root / "cache",
            ("prefix", root / "other"),
        )
        with self.settings(**settings):
            self.assertEqual(check_cache_location_not_exposed(None), [])


class CheckCacheAbsolutePath(SimpleTestCase):
    def test_absolute_path(self):
        """
        Tests the absolute path for a file-based cache.
        
        This function sets up a Django settings environment where the default cache backend is configured to use a file-based cache located at the current working directory. It then calls the `check_file_based_cache_is_absolute` function with a `None` argument and asserts that the returned list is empty, indicating that the cache path is correctly determined to be absolute.
        
        Parameters:
        None
        
        Returns:
        list: A list of errors or issues found during the check. An
        """

        with self.settings(
            CACHES={
                "default": {
                    "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
                    "LOCATION": pathlib.Path.cwd() / "cache",
                },
            }
        ):
            self.assertEqual(check_file_based_cache_is_absolute(None), [])

    def test_relative_path(self):
        with self.settings(
            CACHES={
                "default": {
                    "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
                    "LOCATION": "cache",
                },
            }
        ):
            self.assertEqual(
                check_file_based_cache_is_absolute(None),
                [
                    Warning(
                        "Your 'default' cache LOCATION path is relative. Use an "
                        "absolute path instead.",
                        id="caches.W003",
                    ),
                ],
            )
