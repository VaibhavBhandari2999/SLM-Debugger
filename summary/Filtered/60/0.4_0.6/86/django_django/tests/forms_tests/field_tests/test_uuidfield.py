import uuid

from django.core.exceptions import ValidationError
from django.forms import UUIDField
from django.test import SimpleTestCase


class UUIDFieldTest(SimpleTestCase):

    def test_uuidfield_1(self):
        """
        Tests the UUIDField clean method.
        
        This method tests the clean method of the UUIDField to ensure it correctly converts a string representation of a UUID to a UUID object. The clean method takes a single required parameter, 'value', which is a string representation of a UUID. The method returns a UUID object.
        
        Parameters:
        value (str): A string representation of a UUID.
        
        Returns:
        uuid.UUID: A UUID object corresponding to the input string.
        
        Example:
        >>> field = UUIDField()
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
        field = UUIDField()
        with self.assertRaisesMessage(ValidationError, 'Enter a valid UUID.'):
            field.clean('550e8400')

    def test_uuidfield_4(self):
        """
        Test the UUIDField preparation method.
        
        This function tests the `prepare_value` method of the UUIDField class. It takes a UUID object as input and prepares it for storage or transmission. The input UUID is expected to be in the standard format. The method returns a string representation of the UUID in the format 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx', where each 'x' is a hexadecimal digit.
        
        Parameters:
        value (uuid.UUID): The UUID object to be prepared.
        
        Returns:
        """

        field = UUIDField()
        value = field.prepare_value(uuid.UUID('550e8400e29b41d4a716446655440000'))
        self.assertEqual(value, '550e8400-e29b-41d4-a716-446655440000')
