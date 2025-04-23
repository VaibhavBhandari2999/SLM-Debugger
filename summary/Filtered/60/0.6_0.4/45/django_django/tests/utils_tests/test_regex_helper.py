import unittest

from django.utils import regex_helper


class NormalizeTests(unittest.TestCase):
    def test_empty(self):
        """
        Tests the behavior of the `normalize` function with an empty regular expression pattern.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Behavior:
        - The `normalize` function is called with an empty string pattern.
        - The expected output is a tuple containing an empty string and an empty list.
        - The function asserts that the result of `normalize` matches the expected output.
        
        Notes:
        - This test case is designed to check how the function handles an edge case where the input pattern
        """

        pattern = r""
        expected = [('', [])]
        result = regex_helper.normalize(pattern)
        self.assertEqual(result, expected)

    def test_escape(self):
        """
        Normalize a regular expression pattern to ensure it is properly escaped.
        
        Args:
        pattern (str): The regular expression pattern to be normalized.
        
        Returns:
        tuple: A tuple containing the normalized pattern and an empty list.
        
        This function takes a regular expression pattern and ensures that special characters are properly escaped, which is necessary for the pattern to be interpreted correctly by the regex engine. The function returns a tuple with the normalized pattern and an empty list.
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
