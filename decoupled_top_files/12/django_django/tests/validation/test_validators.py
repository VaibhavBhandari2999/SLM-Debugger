from django.test import SimpleTestCase

from . import ValidationAssertions
from .models import ModelToValidate


class TestModelsWithValidators(ValidationAssertions, SimpleTestCase):
    def test_custom_validator_passes_for_correct_value(self):
        """
        Test that the custom validator passes for the correct value.
        
        This test ensures that the custom validator is correctly applied to the
        `f_with_custom_validator` field of the `ModelToValidate` instance. The
        `full_clean()` method is called to validate the model, and since the value
        42 is expected to pass the validation, `full_clean()` should return None.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - Model
        """

        mtv = ModelToValidate(number=10, name='Some Name', f_with_custom_validator=42,
                              f_with_iterable_of_validators=42)
        self.assertIsNone(mtv.full_clean())

    def test_custom_validator_raises_error_for_incorrect_value(self):
        """
        Tests that the custom validator raises an error when the value of 'f_with_custom_validator' is incorrect.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the custom validator does not raise an error or if the error message is incorrect.
        
        Important Functions:
        - `ModelToValidate`: The model being validated.
        - `full_clean`: Method used to clean and validate the model instance.
        - `assertFailsValidation`: Asserts that the
        """

        mtv = ModelToValidate(number=10, name='Some Name', f_with_custom_validator=12,
                              f_with_iterable_of_validators=42)
        self.assertFailsValidation(mtv.full_clean, ['f_with_custom_validator'])
        self.assertFieldFailsValidationWithMessage(
            mtv.full_clean,
            'f_with_custom_validator',
            ['This is not the answer to life, universe and everything!']
        )

    def test_field_validators_can_be_any_iterable(self):
        """
        Tests that field validators can be any iterable.
        
        This function creates an instance of `ModelToValidate` with specific values for its fields. It then uses the `full_clean` method to validate the model and checks if the validation fails for the field `f_with_iterable_of_validators`. Additionally, it asserts that the validation failure message for this field matches the expected message: 'This is not the answer to life, universe and everything!'.
        """

        mtv = ModelToValidate(number=10, name='Some Name', f_with_custom_validator=42,
                              f_with_iterable_of_validators=12)
        self.assertFailsValidation(mtv.full_clean, ['f_with_iterable_of_validators'])
        self.assertFieldFailsValidationWithMessage(
            mtv.full_clean,
            'f_with_iterable_of_validators',
            ['This is not the answer to life, universe and everything!']
        )
