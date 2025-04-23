import uuid

from django.core.exceptions import ValidationError
from django.forms import UUIDField
from django.test import SimpleTestCase


class UUIDFieldTest(SimpleTestCase):

    def test_uuidfield_1(self):
        field = UUIDField()
        value = field.clean('550e8400e29b41d4a716446655440000')
        self.assertEqual(value, uuid.UUID('550e8400e29b41d4a716446655440000'))

    def test_clean_value_with_dashes(self):
        field = UUIDField()
        value = field.clean('550e8400-e29b-41d4-a716-446655440000')
        self.assertEqual(value, uuid.UUID('550e8400e29b41d4a716446655440000'))

    def test_uuidfield_2(self):
        """
        Tests the behavior of the UUIDField with empty and None inputs.
        
        This function tests the UUIDField to ensure it correctly handles empty strings and None values. The UUIDField is configured with the `required=False` parameter, meaning it should accept both empty strings and None without raising an error.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The UUIDField is instantiated with `required=False`.
        - The function checks if the field's `clean` method returns None for both empty strings and
        """

        field = UUIDField(required=False)
        self.assertIsNone(field.clean(''))
        self.assertIsNone(field.clean(None))

    def test_uuidfield_3(self):
        field = UUIDField()
        with self.assertRaisesMessage(ValidationError, 'Enter a valid UUID.'):
            field.clean('550e8400')

    def test_uuidfield_4(self):
        """
        Test the UUIDField preparation method.
        
        This function tests the `prepare_value` method of the `UUIDField` class. It takes a UUID object as input and prepares it for storage or transmission. The UUID is expected to be in the standard format, and the method should return a string representation of the UUID in the format '550e8400-e29b-41d4-a716-446655440000'.
        """

        field = UUIDField()
        value = field.prepare_value(uuid.UUID('550e8400e29b41d4a716446655440000'))
        self.assertEqual(value, '550e8400-e29b-41d4-a716-446655440000')
