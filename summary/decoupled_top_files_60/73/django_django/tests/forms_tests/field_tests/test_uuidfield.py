import uuid

from django.core.exceptions import ValidationError
from django.forms import UUIDField
from django.test import SimpleTestCase


class UUIDFieldTest(SimpleTestCase):

    def test_uuidfield_1(self):
        """
        Test the UUIDField clean method.
        
        This function tests the clean method of the UUIDField to ensure it correctly converts a string representation of a UUID to a UUID object.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The UUIDField clean method is tested with a specific UUID string.
        - The expected output is a UUID object corresponding to the input string.
        - The test asserts that the cleaned value is equal to the expected UUID object.
        """

        field = UUIDField()
        value = field.clean('550e8400e29b41d4a716446655440000')
        self.assertEqual(value, uuid.UUID('550e8400e29b41d4a716446655440000'))

    def test_clean_value_with_dashes(self):
        field = UUIDField()
        value = field.clean('550e8400-e29b-41d4-a716-446655440000')
        self.assertEqual(value, uuid.UUID('550e8400e29b41d4a716446655440000'))

    def test_uuidfield_2(self):
        field = UUIDField(required=False)
        self.assertIsNone(field.clean(''))
        self.assertIsNone(field.clean(None))

    def test_uuidfield_3(self):
        """
        Tests the UUIDField validation.
        
        This function tests the validation of a UUIDField. It checks if the field raises a ValidationError with the message 'Enter a valid UUID.' when an invalid UUID is provided.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the input is not a valid UUID, a ValidationError is raised with the message 'Enter a valid UUID.'
        """

        field = UUIDField()
        with self.assertRaisesMessage(ValidationError, 'Enter a valid UUID.'):
            field.clean('550e8400')

    def test_uuidfield_4(self):
        """
        Test the UUIDField preparation.
        
        This function tests the `prepare_value` method of the `UUIDField` class. It takes a UUID object as input and prepares it for storage or transmission. The UUID is expected to be in the standard format. The function returns a string representation of the UUID, formatted as 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx', where each 'x' is a hexadecimal digit.
        
        Parameters:
        value (uuid.UUID): The UUID object to be prepared.
        
        Returns:
        """

        field = UUIDField()
        value = field.prepare_value(uuid.UUID('550e8400e29b41d4a716446655440000'))
        self.assertEqual(value, '550e8400-e29b-41d4-a716-446655440000')
