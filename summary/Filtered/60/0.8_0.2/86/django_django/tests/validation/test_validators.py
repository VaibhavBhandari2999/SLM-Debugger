from django.test import SimpleTestCase

from . import ValidationAssertions
from .models import ModelToValidate


class TestModelsWithValidators(ValidationAssertions, SimpleTestCase):
    def test_custom_validator_passes_for_correct_value(self):
        """
        Test that the custom validator passes for a correct value.
        
        This test ensures that the custom validator is correctly applied to the specified field in the model instance.
        The model instance is created with the following parameters:
        - number: An integer value.
        - name: A string value.
        - f_with_custom_validator: An integer value that should pass the custom validator.
        - f_with_iterable_of_validators: An integer value that should pass the iterable of validators.
        
        Parameters:
        None
        
        Returns:
        None
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
        mtv = ModelToValidate(number=10, name='Some Name', f_with_custom_validator=42,
                              f_with_iterable_of_validators=12)
        self.assertFailsValidation(mtv.full_clean, ['f_with_iterable_of_validators'])
        self.assertFieldFailsValidationWithMessage(
            mtv.full_clean,
            'f_with_iterable_of_validators',
            ['This is not the answer to life, universe and everything!']
        )
t
