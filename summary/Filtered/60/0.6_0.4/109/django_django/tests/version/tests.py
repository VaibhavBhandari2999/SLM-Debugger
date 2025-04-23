from unittest import skipUnless

import django.utils.version
from django import get_version
from django.test import SimpleTestCase
from django.utils.version import (
    get_complete_version,
    get_git_changeset,
    get_version_tuple,
)


class VersionTests(SimpleTestCase):
    def test_development(self):
        """
        Tests the development version generation function.
        
        This test checks the behavior of the `get_version` function when a version tuple is provided. The function is expected to return a version string that either includes a development changeset if run within a git repository, or a simple version string if not. The version tuple provided is (1, 4, 0, "alpha", 0), which indicates a version 1.4 with an alpha release and no post-release number. The test ensures that the
        """

        get_git_changeset.cache_clear()
        ver_tuple = (1, 4, 0, "alpha", 0)
        # This will return a different result when it's run within or outside
        # of a git clone: 1.4.devYYYYMMDDHHMMSS or 1.4.
        ver_string = get_version(ver_tuple)
        self.assertRegex(ver_string, r"1\.4(\.dev[0-9]+)?")

    @skipUnless(
        hasattr(django.utils.version, "__file__"),
        "test_development() checks the same when __file__ is already missing, "
        "e.g. in a frozen environments",
    )
    def test_development_no_file(self):
        get_git_changeset.cache_clear()
        version_file = django.utils.version.__file__
        try:
            del django.utils.version.__file__
            self.test_development()
        finally:
            django.utils.version.__file__ = version_file

    def test_releases(self):
        tuples_to_strings = (
            ((1, 4, 0, "alpha", 1), "1.4a1"),
            ((1, 4, 0, "beta", 1), "1.4b1"),
            ((1, 4, 0, "rc", 1), "1.4rc1"),
            ((1, 4, 0, "final", 0), "1.4"),
            ((1, 4, 1, "rc", 2), "1.4.1rc2"),
            ((1, 4, 1, "final", 0), "1.4.1"),
        )
        for ver_tuple, ver_string in tuples_to_strings:
            self.assertEqual(get_version(ver_tuple), ver_string)

    def test_get_version_tuple(self):
        """
        Tests the get_version_tuple function.
        
        This function takes a version string and returns a tuple of integers representing the version numbers.
        Parameters:
        version_str (str): The version string to be converted to a tuple.
        
        Returns:
        tuple: A tuple of integers representing the version numbers.
        
        Test cases:
        - get_version_tuple("1.2.3") should return (1, 2, 3).
        - get_version_tuple("1.2.3b2") should return (1
        """

        self.assertEqual(get_version_tuple("1.2.3"), (1, 2, 3))
        self.assertEqual(get_version_tuple("1.2.3b2"), (1, 2, 3))
        self.assertEqual(get_version_tuple("1.2.3b2.dev0"), (1, 2, 3))

    def test_get_version_invalid_version(self):
        """
        Test the `get_complete_version` function with invalid version inputs.
        
        This function tests the `get_complete_version` function by providing it with invalid version inputs and verifying that an `AssertionError` is raised.
        
        Parameters:
        version (tuple): A tuple representing the version in the format (major, minor, micro, releaselevel, serial).
        
        Returns:
        None: The function should raise an `AssertionError` for invalid inputs.
        
        Test Cases:
        1. Invalid length of the version tuple.
        2.
        """

        tests = [
            # Invalid length.
            (3, 2, 0, "alpha", 1, "20210315111111"),
            # Invalid development status.
            (3, 2, 0, "gamma", 1, "20210315111111"),
        ]
        for version in tests:
            with self.subTest(version=version), self.assertRaises(AssertionError):
                get_complete_version(version)
