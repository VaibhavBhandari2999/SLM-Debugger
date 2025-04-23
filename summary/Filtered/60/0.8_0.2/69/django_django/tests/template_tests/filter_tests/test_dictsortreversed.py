from django.template.defaultfilters import dictsortreversed
from django.test import SimpleTestCase


class FunctionTests(SimpleTestCase):

    def test_sort(self):
        """
        Test the `dictsortreversed` function.
        
        This function sorts a list of dictionaries based on a specified key in descending order.
        
        Parameters:
        - dicts (list): A list of dictionaries to be sorted.
        - key (str): The key in the dictionaries to sort by.
        
        Returns:
        - list: A list of dictionaries sorted in descending order based on the specified key.
        
        Example:
        >>> sorted_dicts = dictsortreversed(
        ...     [{'age': 23, 'name': 'Barbara
        """

        sorted_dicts = dictsortreversed(
            [{'age': 23, 'name': 'Barbara-Ann'},
             {'age': 63, 'name': 'Ra Ra Rasputin'},
             {'name': 'Jonny B Goode', 'age': 18}],
            'age',
        )

        self.assertEqual(
            [sorted(dict.items()) for dict in sorted_dicts],
            [[('age', 63), ('name', 'Ra Ra Rasputin')],
             [('age', 23), ('name', 'Barbara-Ann')],
             [('age', 18), ('name', 'Jonny B Goode')]],
        )

    def test_sort_list_of_tuples(self):
        data = [('a', '42'), ('c', 'string'), ('b', 'foo')]
        expected = [('c', 'string'), ('b', 'foo'), ('a', '42')]
        self.assertEqual(dictsortreversed(data, 0), expected)

    def test_sort_list_of_tuple_like_dicts(self):
        """
        Test sorting a list of dictionary-like objects based on a specific key in reverse order.
        
        Parameters:
        data (list): A list of dictionary-like objects with keys '0' and '1'.
        key (str): The key in the dictionaries to sort by.
        
        Returns:
        list: A new list of dictionary-like objects sorted in reverse order based on the specified key.
        
        Example:
        >>> data = [{'0': 'a', '1': '42'}, {'0': 'c',
        """

        data = [
            {'0': 'a', '1': '42'},
            {'0': 'c', '1': 'string'},
            {'0': 'b', '1': 'foo'},
        ]
        expected = [
            {'0': 'c', '1': 'string'},
            {'0': 'b', '1': 'foo'},
            {'0': 'a', '1': '42'},
        ]
        self.assertEqual(dictsortreversed(data, '0'), expected)

    def test_invalid_values(self):
        """
        If dictsortreversed is passed something other than a list of
        dictionaries, fail silently.
        """
        self.assertEqual(dictsortreversed([1, 2, 3], 'age'), '')
        self.assertEqual(dictsortreversed('Hello!', 'age'), '')
        self.assertEqual(dictsortreversed({'a': 1}, 'age'), '')
        self.assertEqual(dictsortreversed(1, 'age'), '')
self.assertEqual(dictsortreversed(1, 'age'), '')
