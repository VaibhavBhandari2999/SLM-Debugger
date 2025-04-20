import unittest

from django.utils import regex_helper


class NormalizeTests(unittest.TestCase):
    def test_empty(self):
        pattern = r""
        expected = [('', [])]
        result = regex_helper.normalize(pattern)
        self.assertEqual(result, expected)

    def test_escape(self):
        """
        Normalize a regular expression pattern to ensure it is properly escaped.
        
        This function takes a string pattern and normalizes it by escaping any special characters that might be misinterpreted in a regular expression context. The function returns a tuple containing the normalized pattern and an empty list (indicating no additional metadata).
        
        Parameters:
        pattern (str): The regular expression pattern to be normalized.
        
        Returns:
        tuple: A tuple containing the normalized pattern and an empty list.
        
        Example:
        >>> test_escape(r"\\\^\$\
        """

        pattern = r"\\\^\$\.\|\?\*\+\(\)\["
        expected = [('\\^$.|?*+()[', [])]
        result = regex_helper.normalize(pattern)
        self.assertEqual(result, expected)

    def test_group_positional(self):
        pattern = r"(.*)-(.+)"
        expected = [('%(_0)s-%(_1)s', ['_0', '_1'])]
        result = regex_helper.normalize(pattern)
        self.assertEqual(result, expected)

    def test_group_noncapturing(self):
        """
        Function: test_group_noncapturing
        
        This function tests the normalization of a regular expression pattern that includes a non-capturing group.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Description:
        The function `test_group_noncapturing` is designed to test the `normalize` method of the `regex_helper` class. It uses a specific regular expression pattern with a non-capturing group and checks if the `normalize` method returns the expected result. The expected result is a tuple containing
        """

        pattern = r"(?:non-capturing)"
        expected = [('non-capturing', [])]
        result = regex_helper.normalize(pattern)
        self.assertEqual(result, expected)

    def test_group_named(self):
        pattern = r"(?P<first_group_name>.*)-(?P<second_group_name>.*)"
        expected = [('%(first_group_name)s-%(second_group_name)s',
                    ['first_group_name', 'second_group_name'])]
        result = regex_helper.normalize(pattern)
        self.assertEqual(result, expected)

    def test_group_backreference(self):
        pattern = r"(?P<first_group_name>.*)-(?P=first_group_name)"
        expected = [('%(first_group_name)s-%(first_group_name)s',
                    ['first_group_name'])]
        result = regex_helper.normalize(pattern)
        self.assertEqual(result, expected)
