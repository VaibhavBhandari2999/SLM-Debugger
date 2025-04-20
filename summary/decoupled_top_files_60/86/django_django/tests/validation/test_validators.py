from django.test import SimpleTestCase

from . import ValidationAssertions
from .models import ModelToValidate


class TestModelsWithValidators(ValidationAssertions, SimpleTestCase):
    def test_custom_validator_passes_for_correct_value(self):
        """
        Test the custom validator function for a model instance.
        
        This test ensures that the custom validator function passes for the correct value.
        
        Parameters:
        mtv (ModelToValidate): The model instance to be validated.
        
        Returns:
        None: The test asserts that full_clean() does not raise any validation errors.
        """

        mtv = ModelToValidate(number=10, name='Some Name', f_with_custom_validator=42,
                              f_with_iterable_of_validators=42)
        self.assertIsNone(mtv.full_clean())

    def test_custom_validator_raises_error_for_incorrect_value(self):
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
        Test that field validators can be any iterable.
        
        This function tests whether field validators in a model can accept any iterable, including custom validators and iterables of validators. It creates an instance of `ModelToValidate` with specific values for its fields and checks if the validation fails as expected for the field `f_with_iterable_of_validators`.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - `assertFailsValidation`: Verifies that the full_clean method fails validation for the `
        """

        mtv = ModelToValidate(number=10, name='Some Name', f_with_custom_validator=42,
                              f_with_iterable_of_validators=12)
        self.assertFailsValidation(mtv.full_clean, ['f_with_iterable_of_validators'])
        self.assertFieldFailsValidationWithMessage(
            mtv.full_clean,
            'f_with_iterable_of_validators',
            ['This is not the answer to life, universe and everything!']
        )
