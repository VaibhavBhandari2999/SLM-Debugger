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
        Test the custom validator for incorrect values.
        
        This function tests the custom validator on a model instance to ensure it raises a validation error for an incorrect value in the 'f_with_custom_validator' field. The model instance is created with specific values for different fields, and the full_clean method is called to trigger validation. The test checks that the validation error is raised for the specified field and that the error message matches the expected message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError:
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
        Test that field validators can be any iterable.
        
        This function tests the validation of a model field that accepts any iterable as a validator.
        The model instance is created with specific values for various fields, including one field
        that is validated using a custom validator and another field that is validated using an iterable
        of validators.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The `full_clean` method should fail validation for the field `f_with_iterable_of_validators`.
        - The
        """

        mtv = ModelToValidate(number=10, name='Some Name', f_with_custom_validator=42,
                              f_with_iterable_of_validators=12)
        self.assertFailsValidation(mtv.full_clean, ['f_with_iterable_of_validators'])
        self.assertFieldFailsValidationWithMessage(
            mtv.full_clean,
            'f_with_iterable_of_validators',
            ['This is not the answer to life, universe and everything!']
        )
