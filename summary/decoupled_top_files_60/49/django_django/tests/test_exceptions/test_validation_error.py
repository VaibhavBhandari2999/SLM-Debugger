import unittest

from django.core.exceptions import ValidationError


class TestValidationError(unittest.TestCase):
    def test_messages_concatenates_error_dict_values(self):
        """
        Test the concatenation of error dictionary values in a ValidationError.
        
        This function tests the behavior of the ValidationError class when error messages are added to a dictionary and then used to create an exception. The function checks that the error messages are correctly concatenated and sorted.
        
        Parameters:
        message_dict (dict): A dictionary where keys are field names and values are lists of error messages.
        
        Returns:
        None: The function asserts the correctness of the ValidationError messages through assertions.
        
        Steps:
        1. Initialize an empty dictionary `message
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
