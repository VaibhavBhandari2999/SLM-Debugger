import uuid

from django.core.exceptions import ValidationError
from django.forms import UUIDField
from django.test import SimpleTestCase


class UUIDFieldTest(SimpleTestCase):

    def test_uuidfield_1(self):
        """
        Tests the UUIDField clean method.
        
        This method tests the clean method of the UUIDField. It takes a string representation of a UUID and converts it into a UUID object. The input is a string '550e8400e29b41d4a716446655440000'. The output is a UUID object with the same value.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - value
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
        Tests the validation of a UUIDField.
        
        This function tests the validation of a UUIDField by attempting to clean an invalid UUID string. It raises a ValidationError with the message 'Enter a valid UUID.' if the input is not a valid UUID.
        
        Parameters:
        None
        
        Raises:
        ValidationError: If the input '550e8400' is not a valid UUID.
        
        Returns:
        None
        """

        field = UUIDField()
        with self.assertRaisesMessage(ValidationError, 'Enter a valid UUID.'):
            field.clean('550e8400')

    def test_uuidfield_4(self):
        field = UUIDField()
        value = field.prepare_value(uuid.UUID('550e8400e29b41d4a716446655440000'))
        self.assertEqual(value, '550e8400-e29b-41d4-a716-446655440000')
prepare_value(uuid.UUID('550e8400e29b41d4a716446655440000'))
        self.assertEqual(value, '550e8400-e29b-41d4-a716-446655440000')
