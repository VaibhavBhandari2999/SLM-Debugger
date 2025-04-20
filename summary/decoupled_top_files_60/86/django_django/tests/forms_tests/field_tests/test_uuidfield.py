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
        - The test asserts that the output is indeed the expected UUID object.
        """

        field = UUIDField()
        value = field.clean('550e8400e29b41d4a716446655440000')
        self.assertEqual(value, uuid.UUID('550e8400e29b41d4a716446655440000'))

    def test_clean_value_with_dashes(self):
        """
        Tests the clean_value_with_dashes method of the UUIDField class.
        
        This method is responsible for cleaning and validating a string input to ensure it is a valid UUID. The input is expected to be a string representation of a UUID with or without hyphens. The method should return a uuid.UUID object if the input is valid, or raise a ValidationError if the input is invalid.
        
        Parameters:
        None (This is a test method and does not take any parameters)
        
        Returns:
        None (The test
        """

        field = UUIDField()
        value = field.clean('550e8400-e29b-41d4-a716-446655440000')
        self.assertEqual(value, uuid.UUID('550e8400e29b41d4a716446655440000'))

    def test_uuidfield_2(self):
        field = UUIDField(required=False)
        self.assertIsNone(field.clean(''))
        self.assertIsNone(field.clean(None))

    def test_uuidfield_3(self):
        field = UUIDField()
        with self.assertRaisesMessage(ValidationError, 'Enter a valid UUID.'):
            field.clean('550e8400')

    def test_uuidfield_4(self):
        """
        Test the UUIDField's prepare_value method.
        
        This method takes a UUID object and returns a string representation of it in the format '550e8400-e29b-41d4-a716-446655440000'.
        
        Parameters:
        field (UUIDField): The UUIDField instance being tested.
        
        Returns:
        str: The string representation of the provided UUID object.
        
        Example:
        >>> field = UUIDField()
        """

        field = UUIDField()
        value = field.prepare_value(uuid.UUID('550e8400e29b41d4a716446655440000'))
        self.assertEqual(value, '550e8400-e29b-41d4-a716-446655440000')
Equal(value, '550e8400-e29b-41d4-a716-446655440000')
    self.assertEqual(value, '550e8400-e29b-41d4-a716-446655440000')
