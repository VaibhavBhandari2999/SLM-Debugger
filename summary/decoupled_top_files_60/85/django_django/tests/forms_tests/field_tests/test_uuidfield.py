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
        
        This method is used to clean and validate a UUID string. The function takes a single string argument 'value' which is expected to be a valid UUID with or without dashes. The function returns a uuid.UUID object with dashes removed.
        
        Parameters:
        value (str): A UUID string with or without dashes.
        
        Returns:
        uuid.UUID: A UUID object with dashes removed.
        
        Example:
        >>> field = UUIDField()
        >>> field
        """

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
        
        This function tests the validation of a UUIDField. It creates an instance of the UUIDField and then attempts to clean an invalid UUID string. If the string is not a valid UUID, a ValidationError should be raised with the message 'Enter a valid UUID.'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the input string '550e8400' is not a valid UUID, a ValidationError is raised with
        """

        field = UUIDField()
        with self.assertRaisesMessage(ValidationError, 'Enter a valid UUID.'):
            field.clean('550e8400')

    def test_uuidfield_4(self):
        field = UUIDField()
        value = field.prepare_value(uuid.UUID('550e8400e29b41d4a716446655440000'))
        self.assertEqual(value, '550e8400-e29b-41d4-a716-446655440000')
