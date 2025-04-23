from django.template.defaultfilters import dictsortreversed
from django.test import SimpleTestCase


class FunctionTests(SimpleTestCase):

    def test_sort(self):
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
        """
        Function to test sorting a list of tuples in reverse order based on the first element.
        
        Parameters:
        data (list of tuples): A list of tuples where each tuple contains two elements.
        
        Returns:
        list of tuples: The sorted list of tuples in reverse order based on the first element of each tuple.
        
        Example:
        >>> test_sort_list_of_tuples([('a', '42'), ('c', 'string'), ('b', 'foo')])
        [('c', 'string'), ('b', '
        """

        data = [('a', '42'), ('c', 'string'), ('b', 'foo')]
        expected = [('c', 'string'), ('b', 'foo'), ('a', '42')]
        self.assertEqual(dictsortreversed(data, 0), expected)

    def test_sort_list_of_tuple_like_dicts(self):
        """
        Test sorting a list of dictionary-like objects by a specific key in descending order.
        
        Parameters:
        data (list): A list of dictionary-like objects, where each dictionary has keys '0' and '1'.
        key (str): The key in the dictionaries by which to sort the list.
        
        Returns:
        list: A new list of dictionary-like objects sorted in descending order based on the specified key.
        
        Example:
        Given the input:
        data = [
        {'0': 'a', '
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
elf.assertEqual(dictsortreversed(1, 'age'), '')
