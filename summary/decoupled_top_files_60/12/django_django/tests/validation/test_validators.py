from django.test import SimpleTestCase

from . import ValidationAssertions
from .models import ModelToValidate


class TestModelsWithValidators(ValidationAssertions, SimpleTestCase):
    def test_custom_validator_passes_for_correct_value(self):
        """
        Test that a custom validator passes for a correct value.
        
        This test ensures that the custom validator is correctly applied to the specified field in the model.
        The model instance is validated using `full_clean()` and no errors are expected.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Attributes:
        - `number`: An integer value.
        - `name`: A string value.
        - `f_with_custom_validator`: An integer value that should pass the custom validator.
        - `f_with_iter
        """

        mtv = ModelToValidate(number=10, name='Some Name', f_with_custom_validator=42,
                              f_with_iterable_of_validators=42)
        self.assertIsNone(mtv.full_clean())

    def test_custom_validator_raises_error_for_incorrect_value(self):
        """
        Test the custom validator for incorrect values.
        
        This function validates a model instance, `ModelToValidate`, to ensure that the custom validator raises an error for the field `f_with_custom_validator`. The custom validator checks if the value is 42, which is the answer to life, the universe, and everything. If the value is not 42, the validator raises a validation error.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the custom validator does not
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
the answer to life, universe and everything!']
        )
