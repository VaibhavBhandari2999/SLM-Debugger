from django.test import SimpleTestCase

from . import ValidationAssertions
from .models import ModelToValidate


class TestModelsWithValidators(ValidationAssertions, SimpleTestCase):
    def test_custom_validator_passes_for_correct_value(self):
        mtv = ModelToValidate(
            number=10,
            name="Some Name",
            f_with_custom_validator=42,
            f_with_iterable_of_validators=42,
        )
        self.assertIsNone(mtv.full_clean())

    def test_custom_validator_raises_error_for_incorrect_value(self):
        """
        Test the custom validator for incorrect values.
        
        This function tests the custom validator for the `f_with_custom_validator` field in the `ModelToValidate` class. It ensures that the validator raises an error when the value is incorrect.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the validation fails to raise the expected error.
        
        Usage:
        This function is used to verify that the custom validator for the `f_with_custom_validator` field in the `ModelToValidate`
        """

        mtv = ModelToValidate(
            number=10,
            name="Some Name",
            f_with_custom_validator=12,
            f_with_iterable_of_validators=42,
        )
        self.assertFailsValidation(mtv.full_clean, ["f_with_custom_validator"])
        self.assertFieldFailsValidationWithMessage(
            mtv.full_clean,
            "f_with_custom_validator",
            ["This is not the answer to life, universe and everything!"],
        )

    def test_field_validators_can_be_any_iterable(self):
        """
        Test that field validators can be any iterable.
        
        This function tests the validation of a model instance with fields that have custom validators and validators defined as an iterable. The function creates an instance of `ModelToValidate` with specific values for its fields and then checks if the validation fails as expected for the fields with iterable validators.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The `f_with_iterable_of_validators` field should fail validation.
        - The `f_with_iter
        """

        mtv = ModelToValidate(
            number=10,
            name="Some Name",
            f_with_custom_validator=42,
            f_with_iterable_of_validators=12,
        )
        self.assertFailsValidation(mtv.full_clean, ["f_with_iterable_of_validators"])
        self.assertFieldFailsValidationWithMessage(
            mtv.full_clean,
            "f_with_iterable_of_validators",
            ["This is not the answer to life, universe and everything!"],
        )
