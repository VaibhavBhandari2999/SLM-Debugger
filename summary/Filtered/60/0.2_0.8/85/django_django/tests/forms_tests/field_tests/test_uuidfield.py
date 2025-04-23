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
        Tests the behavior of the UUIDField when provided with empty or None values.
        
        This function tests the UUIDField to ensure that it correctly handles empty strings and None values by returning None.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The UUIDField is tested for its ability to accept empty strings and None values.
        - The function asserts that the clean method of the UUIDField returns None when given an empty string or None.
        """

        field = UUIDField(required=False)
        self.assertIsNone(field.clean(''))
        self.assertIsNone(field.clean(None))

    def test_uuidfield_3(self):
        """
        Tests the validation of UUIDField.
        
        This function tests the validation of a UUIDField. It creates an instance of the UUIDField and attempts to clean an invalid UUID string. If the string is not a valid UUID, a ValidationError is expected to be raised with the message 'Enter a valid UUID.'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the input string is not a valid UUID, a ValidationError is raised with the message 'Enter a valid UUID.'.
        """

        field = UUIDField()
        with self.assertRaisesMessage(ValidationError, 'Enter a valid UUID.'):
            field.clean('550e8400')

    def test_uuidfield_4(self):
        field = UUIDField()
        value = field.prepare_value(uuid.UUID('550e8400e29b41d4a716446655440000'))
        self.assertEqual(value, '550e8400-e29b-41d4-a716-446655440000')
