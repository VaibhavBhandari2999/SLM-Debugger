import unittest

from django.core.exceptions import ValidationError


class TestValidationError(unittest.TestCase):
    def test_messages_concatenates_error_dict_values(self):
        """
        Test the concatenation of error dictionary values in ValidationError messages.
        
        This function tests the behavior of the ValidationError class when error messages are concatenated from a dictionary. It initializes an empty dictionary and creates a ValidationError object with this dictionary. The function then updates the dictionary with error messages for different fields and checks if the ValidationError object correctly concatenates these messages.
        
        Parameters:
        None
        
        Returns:
        None
        
        Steps:
        1. Initialize an empty dictionary `message_dict`.
        2. Create a ValidationError object `exception` with
        """

        message_dict = {}
        exception = ValidationError(message_dict)
        self.assertEqual(sorted(exception.messages), [])
        message_dict['field1'] = ['E1', 'E2']
        exception = ValidationError(message_dict)
        self.assertEqual(sorted(exception.messages), ['E1', 'E2'])
        message_dict['field2'] = ['E3', 'E4']
        exception = ValidationError(message_dict)
        self.assertEqual(sorted(exception.messages), ['E1', 'E2', 'E3', 'E4'])
