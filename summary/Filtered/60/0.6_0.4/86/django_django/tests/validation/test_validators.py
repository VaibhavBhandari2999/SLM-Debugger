from django.test import SimpleTestCase

from . import ValidationAssertions
from .models import ModelToValidate


class TestModelsWithValidators(ValidationAssertions, SimpleTestCase):
    def test_custom_validator_passes_for_correct_value(self):
        """
        Test that the custom validator passes for a correct value.
        
        This test ensures that the custom validator is correctly applied to the specified field in the model. The model instance is created with a valid value for the field that triggers the custom validator. The `full_clean` method is then called to validate the model. If the custom validator is correctly implemented, `full_clean` should not raise any validation errors.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - `mtv`: An
        """

        mtv = ModelToValidate(number=10, name='Some Name', f_with_custom_validator=42,
                              f_with_iterable_of_validators=42)
        self.assertIsNone(mtv.full_clean())

    def test_custom_validator_raises_error_for_incorrect_value(self):
        """
        Test the custom validator for incorrect values.
        
        This function validates a model instance with a custom validator that checks if a specific field value is equal to 42. If the value is incorrect, the function asserts that the validation fails and provides a specific error message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the validation does not fail as expected or the error message does not match the expected message.
        
        Key Parameters:
        - mtv (ModelToValidate): The model
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
        mtv = ModelToValidate(number=10, name='Some Name', f_with_custom_validator=42,
                              f_with_iterable_of_validators=12)
        self.assertFailsValidation(mtv.full_clean, ['f_with_iterable_of_validators'])
        self.assertFieldFailsValidationWithMessage(
            mtv.full_clean,
            'f_with_iterable_of_validators',
            ['This is not the answer to life, universe and everything!']
        )
