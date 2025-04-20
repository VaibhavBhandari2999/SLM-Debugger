import uuid

from django.core.exceptions import ValidationError
from django.forms import UUIDField
from django.test import SimpleTestCase


class UUIDFieldTest(SimpleTestCase):
    def test_uuidfield_1(self):
        """
        Tests the UUIDField clean method.
        
        This method tests the clean method of the UUIDField. It takes a string representation of a UUID and converts it into a UUID object. The input is a string and the output is a uuid.UUID object.
        
        Parameters:
        self: The instance of the test case.
        
        Returns:
        None: This method does not return anything. It asserts the equality of the cleaned value with the expected UUID object.
        """

        field = UUIDField()
        value = field.clean("550e8400e29b41d4a716446655440000")
        self.assertEqual(value, uuid.UUID("550e8400e29b41d4a716446655440000"))

    def test_clean_value_with_dashes(self):
        """
        Tests the `clean` method of the `UUIDField` class for handling values with dashes.
        
        This method verifies that the `clean` method correctly processes a string with dashes and returns a `uuid.UUID` object without dashes.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The input value is a string with dashes representing a UUID.
        - The `clean` method removes dashes from the string.
        - The output is a `uuid.UUID` object without dashes.
        
        Example
        """

        field = UUIDField()
        value = field.clean("550e8400-e29b-41d4-a716-446655440000")
        self.assertEqual(value, uuid.UUID("550e8400e29b41d4a716446655440000"))

    def test_uuidfield_2(self):
        field = UUIDField(required=False)
        self.assertIsNone(field.clean(""))
        self.assertIsNone(field.clean(None))

    def test_uuidfield_3(self):
        field = UUIDField()
        with self.assertRaisesMessage(ValidationError, "Enter a valid UUID."):
            field.clean("550e8400")

    def test_uuidfield_4(self):
        """
        Tests the UUIDField preparation method.
        
        This function tests the `prepare_value` method of the `UUIDField` class. It takes a UUID object as input and prepares it for storage or transmission. The UUID is expected to be in the standard format and is converted to a string representation with hyphens. The function asserts that the prepared value matches the expected string format.
        
        Parameters:
        uuid.UUID: The UUID object to be prepared.
        
        Returns:
        str: The string representation of the UUID with hy
        """

        field = UUIDField()
        value = field.prepare_value(uuid.UUID("550e8400e29b41d4a716446655440000"))
        self.assertEqual(value, "550e8400-e29b-41d4-a716-446655440000")
