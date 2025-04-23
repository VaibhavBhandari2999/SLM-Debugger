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
        """
        Tests the clean_value_with_dashes method of the UUIDField class.
        
        This method is responsible for cleaning and validating a UUID string. The input is a string representation of a UUID, which may contain hyphens. The method should remove any hyphens and return a valid UUID object.
        
        Parameters:
        value (str): A string representation of a UUID, possibly with hyphens.
        
        Returns:
        uuid.UUID: A UUID object with hyphens removed.
        
        Example:
        >>> field = UUID
        """

        field = UUIDField()
        value = field.clean('550e8400-e29b-41d4-a716-446655440000')
        self.assertEqual(value, uuid.UUID('550e8400e29b41d4a716446655440000'))

    def test_uuidfield_2(self):
        """
        Tests the behavior of the UUIDField with empty and None inputs.
        
        This function tests the UUIDField to ensure it correctly handles empty strings and None values. The UUIDField is configured with the `required=False` parameter, meaning it should accept both empty strings and None without raising an error.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Points:
        - The UUIDField is set to be non-optional (not required).
        - The function verifies that the field does not raise an error when given an
        """

        field = UUIDField(required=False)
        self.assertIsNone(field.clean(''))
        self.assertIsNone(field.clean(None))

    def test_uuidfield_3(self):
        field = UUIDField()
        with self.assertRaisesMessage(ValidationError, 'Enter a valid UUID.'):
            field.clean('550e8400')

    def test_uuidfield_4(self):
        field = UUIDField()
        value = field.prepare_value(uuid.UUID('550e8400e29b41d4a716446655440000'))
        self.assertEqual(value, '550e8400-e29b-41d4-a716-446655440000')
