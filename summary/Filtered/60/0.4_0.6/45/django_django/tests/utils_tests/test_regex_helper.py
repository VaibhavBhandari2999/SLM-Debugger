import unittest

from django.utils import regex_helper


class NormalizeTests(unittest.TestCase):
    def test_empty(self):
        """
        Function: test_empty
        Summary: Tests the normalization of an empty regex pattern.
        Parameters:
        - pattern (str): The regex pattern to be normalized. In this case, an empty string.
        Keywords:
        - None
        Returns:
        - None: This function is a test case and does not return any value. It asserts the correctness of the `normalize` function from `regex_helper`.
        Details:
        This function checks if the `normalize` function from the `regex
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
        """
        Tests the normalization of a regular expression pattern with positional groups.
        
        This function checks if the provided regular expression pattern is correctly normalized into a tuple containing the formatted pattern and a list of group names.
        
        Parameters:
        None
        
        Returns:
        None
        
        Example:
        Given the pattern "(.*)-(.*)" as input, the function should return [('%(_0)s-%(_1)s', ['_0', '_1'])], indicating that the pattern has been correctly normalized with group names '_0' and
        """

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
