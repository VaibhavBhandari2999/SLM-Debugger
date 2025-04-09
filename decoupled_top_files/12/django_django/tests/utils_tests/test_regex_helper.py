import unittest

from django.utils import regex_helper


class NormalizeTests(unittest.TestCase):
    def test_empty(self):
        """
        Normalize an empty regular expression pattern.
        
        Args:
        pattern (str): The input regular expression pattern, which is an empty string ("").
        
        Returns:
        tuple: A tuple containing the normalized pattern and an empty list.
        - pattern (str): The normalized pattern, which remains an empty string ("").
        - matches (list): An empty list indicating no matches were found.
        """

        pattern = r""
        expected = [('', [])]
        result = regex_helper.normalize(pattern)
        self.assertEqual(result, expected)

    def test_escape(self):
        """
        Normalize a regular expression pattern by escaping special characters.
        
        Args:
        pattern (str): The regular expression pattern to be normalized.
        
        Returns:
        tuple: A tuple containing the normalized pattern and an empty list.
        
        Example:
        >>> test_escape(r"\\\^\$\.\|\?\*\+\(\)\[]")
        (('\\^$.|?*+()[', []),)
        """

        pattern = r"\\\^\$\.\|\?\*\+\(\)\["
        expected = [('\\^$.|?*+()[', [])]
        result = regex_helper.normalize(pattern)
        self.assertEqual(result, expected)

    def test_group_positional(self):
        """
        Normalize a regular expression pattern.
        
        Args:
        pattern (str): The regular expression pattern to be normalized.
        
        Returns:
        list: A list containing the normalized pattern and a list of captured groups.
        
        Example:
        >>> pattern = r"(.*)-(.+)"
        >>> expected = [('%(_0)s-%(_1)s', ['_0', '_1'])]
        >>> result = regex_helper.normalize(pattern)
        >>> result
        [('%(_0)s-%(_1)s
        """

        pattern = r"(.*)-(.+)"
        expected = [('%(_0)s-%(_1)s', ['_0', '_1'])]
        result = regex_helper.normalize(pattern)
        self.assertEqual(result, expected)

    def test_group_noncapturing(self):
        """
        Normalize a regular expression pattern with a non-capturing group.
        
        Args:
        pattern (str): The regular expression pattern containing a non-capturing group.
        
        Returns:
        list: A tuple containing the normalized pattern and an empty list of captured groups.
        """

        pattern = r"(?:non-capturing)"
        expected = [('non-capturing', [])]
        result = regex_helper.normalize(pattern)
        self.assertEqual(result, expected)

    def test_group_named(self):
        """
        Normalize a regular expression pattern with named groups.
        
        Args:
        pattern (str): The regular expression pattern to be normalized.
        
        Returns:
        list: A list containing a tuple with the normalized pattern and a list of group names.
        
        Example:
        >>> pattern = r"(?P<first_group_name>.*)-(?P<second_group_name>.*)"
        >>> expected = [('%(first_group_name)s-%(second_group_name)s',
        ...              ['first_group_name',
        """

        pattern = r"(?P<first_group_name>.*)-(?P<second_group_name>.*)"
        expected = [('%(first_group_name)s-%(second_group_name)s',
                    ['first_group_name', 'second_group_name'])]
        result = regex_helper.normalize(pattern)
        self.assertEqual(result, expected)

    def test_group_backreference(self):
        """
        Normalize a regular expression with named backreferences.
        
        Args:
        pattern (str): The regular expression pattern containing named
        backreferences.
        
        Returns:
        tuple: A tuple containing the normalized pattern and a list of
        group names.
        
        Example:
        >>> pattern = r"(?P<first_group_name>.*)-(?P=first_group_name)"
        >>> regex_helper.normalize(pattern)
        (('%(first_group_name)s-%(first_group_name)s', ['first_group_name
        """

        pattern = r"(?P<first_group_name>.*)-(?P=first_group_name)"
        expected = [('%(first_group_name)s-%(first_group_name)s',
                    ['first_group_name'])]
        result = regex_helper.normalize(pattern)
        self.assertEqual(result, expected)
