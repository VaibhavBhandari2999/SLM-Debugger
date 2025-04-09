import uuid

from django.core.exceptions import ValidationError
from django.forms import UUIDField
from django.test import SimpleTestCase


class UUIDFieldTest(SimpleTestCase):
    def test_uuidfield_1(self):
        """
        Tests the clean method of the UUIDField class. The function takes a string representation of a UUID and returns a uuid.UUID object after cleaning it. The input is a string '550e8400e29b41d4a716446655440000' and the output is the corresponding uuid.UUID object.
        """

        field = UUIDField()
        value = field.clean("550e8400e29b41d4a716446655440000")
        self.assertEqual(value, uuid.UUID("550e8400e29b41d4a716446655440000"))

    def test_clean_value_with_dashes(self):
        """
        Tests the `clean` method of the `UUIDField` class for handling values with dashes.
        
        This method verifies that the `clean` method correctly processes a string representation of a UUID with dashes and returns a `uuid.UUID` object without the dashes.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `UUIDField.clean`: Cleans and validates the input value.
        - `uuid.UUID`: Converts the cleaned string into a UUID object without dashes.
        
        Input
        """

        field = UUIDField()
        value = field.clean("550e8400-e29b-41d4-a716-446655440000")
        self.assertEqual(value, uuid.UUID("550e8400e29b41d4a716446655440000"))

    def test_uuidfield_2(self):
        """
        Tests the behavior of the UUIDField when cleaning empty or null inputs.
        
        This function tests the UUIDField with two scenarios: cleaning an empty string and cleaning a null value (None). The UUIDField is configured to be optional (required=False). For both cases, the function asserts that the clean method returns None, indicating that it correctly handles these types of inputs without raising errors.
        """

        field = UUIDField(required=False)
        self.assertIsNone(field.clean(""))
        self.assertIsNone(field.clean(None))

    def test_uuidfield_3(self):
        """
        Tests the validation of a UUIDField. The function creates an instance of the UUIDField and attempts to clean an invalid UUID string '550e8400'. It raises a ValidationError with the message 'Enter a valid UUID.' if the input is not a valid UUID.
        """

        field = UUIDField()
        with self.assertRaisesMessage(ValidationError, "Enter a valid UUID."):
            field.clean("550e8400")

    def test_uuidfield_4(self):
        """
        Tests the preparation of a UUID value using the UUIDField.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `UUIDField.prepare_value`: Prepares the given UUID value for storage or transmission.
        
        Input Variables:
        - `uuid.UUID("550e8400e29b41d4a716446655440000")`: The UUID object to be prepared.
        
        Output
        """

        field = UUIDField()
        value = field.prepare_value(uuid.UUID("550e8400e29b41d4a716446655440000"))
        self.assertEqual(value, "550e8400-e29b-41d4-a716-446655440000")
