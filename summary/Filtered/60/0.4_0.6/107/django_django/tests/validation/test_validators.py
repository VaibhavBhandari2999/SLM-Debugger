from django.test import SimpleTestCase

from . import ValidationAssertions
from .models import ModelToValidate


class TestModelsWithValidators(ValidationAssertions, SimpleTestCase):
    def test_custom_validator_passes_for_correct_value(self):
        """
        Test that the custom validator passes for a correct value.
        
        This test ensures that the custom validator and validators from an iterable of validators
        function correctly when provided with valid input values.
        
        Parameters:
        mtv (ModelToValidate): An instance of the ModelToValidate class with the following attributes set:
        - number: An integer value (10 in this case).
        - name: A string value ("Some Name" in this case).
        - f_with_custom_validator: An integer value (4
        """

        mtv = ModelToValidate(
            number=10,
            name="Some Name",
            f_with_custom_validator=42,
            f_with_iterable_of_validators=42,
        )
        self.assertIsNone(mtv.full_clean())

    def test_custom_validator_raises_error_for_incorrect_value(self):
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
 life, universe and everything!"],
        )
