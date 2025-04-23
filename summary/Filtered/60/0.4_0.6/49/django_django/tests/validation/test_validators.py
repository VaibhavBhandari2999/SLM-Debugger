from django.test import SimpleTestCase

from . import ValidationAssertions
from .models import ModelToValidate


class TestModelsWithValidators(ValidationAssertions, SimpleTestCase):
    def test_custom_validator_passes_for_correct_value(self):
        mtv = ModelToValidate(number=10, name='Some Name', f_with_custom_validator=42,
                              f_with_iterable_of_validators=42)
        self.assertIsNone(mtv.full_clean())

    def test_custom_validator_raises_error_for_incorrect_value(self):
        """
        Tests the custom validator for a model field.
        
        This function validates that the custom validator raises an error when the value is incorrect. The model instance `ModelToValidate` is created with specific values for its fields. The `full_clean` method is called to check for validation errors. The function asserts that the validation fails for the field `f_with_custom_validator` and that the error message matches the expected message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the validation
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
