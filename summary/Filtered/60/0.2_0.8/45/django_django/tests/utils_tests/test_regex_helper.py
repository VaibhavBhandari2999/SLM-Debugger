import unittest

from django.utils import regex_helper


class NormalizeTests(unittest.TestCase):
    def test_empty(self):
        """
        Function: test_empty
        Summary: Tests the normalization of an empty regular expression pattern.
        Parameters: None
        Key Parameters:
        - pattern (str): The regular expression pattern to be normalized. In this case, an empty string.
        - expected (list): The expected result after normalization, which is a list containing a tuple with an empty string and an empty list.
        Keywords: None
        Returns: None
        Details: This function is used to verify that the `normalize` function from the `regex
        """

        pattern = r""
        expected = [('', [])]
        result = regex_helper.normalize(pattern)
        self.assertEqual(result, expected)

    def test_escape(self):
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
        pattern = r"(?:non-capturing)"
        expected = [('non-capturing', [])]
        result = regex_helper.normalize(pattern)
        self.assertEqual(result, expected)

    def test_group_named(self):
        """
        Normalize a regular expression pattern with named groups.
        
        This function takes a regular expression pattern with named groups and returns a normalized version of the pattern along with the list of group names.
        
        Parameters:
        pattern (str): The regular expression pattern with named groups.
        
        Returns:
        list: A list containing a tuple with the normalized pattern and a list of group names.
        
        Example:
        >>> pattern = r"(?P<first_group_name>.*)-(?P<second_group_name>.*)"
        >>> expected
        """

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
