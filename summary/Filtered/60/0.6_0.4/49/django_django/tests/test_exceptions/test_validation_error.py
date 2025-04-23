import unittest

from django.core.exceptions import ValidationError


class TestValidationError(unittest.TestCase):
    def test_messages_concatenates_error_dict_values(self):
        """
        Test the concatenation of error dictionary values in ValidationError messages.
        
        This function tests the behavior of the ValidationError class when error messages are added to a dictionary and then used to create an exception. It checks if the messages are correctly concatenated and sorted.
        
        Parameters:
        None
        
        Returns:
        None
        
        Steps:
        1. Initialize an empty dictionary `message_dict`.
        2. Create a ValidationError object using the `message_dict`.
        3. Assert that the sorted list of messages is empty.
        4. Add error messages to
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
