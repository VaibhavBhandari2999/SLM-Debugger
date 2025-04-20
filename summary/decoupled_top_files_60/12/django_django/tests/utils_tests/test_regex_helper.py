import unittest

from django.utils import regex_helper


class NormalizeTests(unittest.TestCase):
    def test_empty(self):
        """
        Normalize an empty regular expression pattern.
        
        This function takes an empty regular expression pattern and normalizes it according to predefined rules. The function returns a tuple containing the normalized pattern and a list of any warnings generated during the normalization process.
        
        Parameters:
        pattern (str): The regular expression pattern to be normalized. In this case, the pattern is an empty string.
        
        Returns:
        tuple: A tuple containing the normalized pattern (str) and a list of warnings (list).
        
        Example:
        >>> test_empty()
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
        Tests the normalization of a regular expression pattern.
        
        This function checks if the provided regular expression pattern is correctly normalized. The pattern is expected to contain named groups. The function takes a single argument, `pattern`, which is a string representing the regular expression. The function returns a list of tuples, where each tuple contains the normalized pattern string and a list of the group names.
        
        Args:
        pattern (str): The regular expression pattern to be normalized.
        
        Returns:
        list: A list of tuples, where
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
that same group. The function returns a tuple containing the normalized pattern and a list of group names.
        
        Parameters:
        pattern (str): The regular expression pattern to be normalized, which must include a named backreference.
        
        Returns:
        tuple: A tuple where the first element is the normalized pattern and
        """

        pattern = r"(?P<first_group_name>.*)-(?P=first_group_name)"
        expected = [('%(first_group_name)s-%(first_group_name)s',
                    ['first_group_name'])]
        result = regex_helper.normalize(pattern)
        self.assertEqual(result, expected)
