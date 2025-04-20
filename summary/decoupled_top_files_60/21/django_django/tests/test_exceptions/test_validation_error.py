import unittest

from django.core.exceptions import ValidationError


class TestValidationError(unittest.TestCase):
    def test_messages_concatenates_error_dict_values(self):
        """
        Tests the concatenation of error dictionary values in a ValidationError.
        
        This function checks the behavior of the ValidationError class when error messages are added to a dictionary and then used to create an instance of ValidationError. It verifies that the error messages are correctly concatenated and sorted.
        
        Parameters:
        None
        
        Returns:
        None
        
        Steps:
        1. Initializes an empty dictionary `message_dict`.
        2. Creates a ValidationError instance using the empty dictionary and asserts that the messages list is empty.
        3. Adds two error messages 'E
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
