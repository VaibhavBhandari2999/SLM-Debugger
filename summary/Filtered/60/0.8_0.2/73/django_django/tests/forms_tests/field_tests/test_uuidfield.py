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
        
        This function tests the UUIDField to ensure it correctly handles empty strings and None values. The UUIDField is configured with the `required` parameter set to False.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The UUIDField is expected to return None when given an empty string ('') or None as input.
        - The field is configured to allow None values without raising an error.
        """

        field = UUIDField(required=False)
        self.assertIsNone(field.clean(''))
        self.assertIsNone(field.clean(None))

    def test_uuidfield_3(self):
        """
        Tests the behavior of the UUIDField in the context of validation.
        
        This function tests the UUIDField's validation mechanism by attempting to clean an invalid UUID string. It expects to raise a ValidationError with a specific error message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the input string '550e8400' is not a valid UUID, the function will raise a ValidationError with the message 'Enter a valid UUID.'.
        
        Note:
        The function uses
        """

        field = UUIDField()
        with self.assertRaisesMessage(ValidationError, 'Enter a valid UUID.'):
            field.clean('550e8400')

    def test_uuidfield_4(self):
        field = UUIDField()
        value = field.prepare_value(uuid.UUID('550e8400e29b41d4a716446655440000'))
        self.assertEqual(value, '550e8400-e29b-41d4-a716-446655440000')
