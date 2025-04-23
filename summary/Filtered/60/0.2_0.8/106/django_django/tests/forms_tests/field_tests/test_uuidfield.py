import uuid

from django.core.exceptions import ValidationError
from django.forms import UUIDField
from django.test import SimpleTestCase


class UUIDFieldTest(SimpleTestCase):
    def test_uuidfield_1(self):
        """
        Tests the UUIDField clean method.
        
        This function tests the clean method of the UUIDField. It takes a string representation of a UUID as input and validates that the clean method correctly converts it to a uuid.UUID object. The input is a string "550e8400e29b41d4a716446655440000" and the expected output is the corresponding uuid.UUID object.
        
        Parameters:
        None
        
        Returns:
        """

        field = UUIDField()
        value = field.clean("550e8400e29b41d4a716446655440000")
        self.assertEqual(value, uuid.UUID("550e8400e29b41d4a716446655440000"))

    def test_clean_value_with_dashes(self):
        field = UUIDField()
        value = field.clean("550e8400-e29b-41d4-a716-446655440000")
        self.assertEqual(value, uuid.UUID("550e8400e29b41d4a716446655440000"))

    def test_uuidfield_2(self):
        field = UUIDField(required=False)
        self.assertIsNone(field.clean(""))
        self.assertIsNone(field.clean(None))

    def test_uuidfield_3(self):
        """
        Tests the UUIDField validation.
        
        This function tests the validation of a UUIDField. It creates an instance of the UUIDField and attempts to clean an invalid UUID string. If the string is not a valid UUID, a ValidationError with the message "Enter a valid UUID." is expected.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the input string is not a valid UUID, a ValidationError is raised with the message "Enter a valid UUID."
        """

        field = UUIDField()
        with self.assertRaisesMessage(ValidationError, "Enter a valid UUID."):
            field.clean("550e8400")

    def test_uuidfield_4(self):
        field = UUIDField()
        value = field.prepare_value(uuid.UUID("550e8400e29b41d4a716446655440000"))
        self.assertEqual(value, "550e8400-e29b-41d4-a716-446655440000")
