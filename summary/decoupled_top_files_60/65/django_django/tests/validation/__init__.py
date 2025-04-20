from django.core.exceptions import ValidationError


class ValidationAssertions:
    def assertFailsValidation(self, clean, failed_fields, **kwargs):
        """
        Asserts that the provided `clean` function fails validation with the specified `failed_fields`.
        
        Parameters:
        clean (function): The clean function to be tested.
        failed_fields (list): A list of field names that are expected to fail validation.
        **kwargs: Additional keyword arguments to be passed to the `clean` function.
        
        Raises:
        ValidationError: If the `clean` function does not raise a ValidationError or if the failed fields do not match the expected ones.
        
        Returns:
        None
        """

        with self.assertRaises(ValidationError) as cm:
            clean(**kwargs)
        self.assertEqual(sorted(failed_fields), sorted(cm.exception.message_dict))

    def assertFieldFailsValidationWithMessage(self, clean, field_name, message):
        """
        Assert that a model instance fails validation for a specific field with a given error message.
        
        Parameters:
        clean (function): A callable that performs the model instance's clean method.
        field_name (str): The name of the field to check for validation failure.
        message (str): The expected error message for the specified field.
        
        Raises:
        ValidationError: If the validation does not fail for the specified field or if the error message does not match the expected one.
        
        This function is used to test that
        """

        with self.assertRaises(ValidationError) as cm:
            clean()
        self.assertIn(field_name, cm.exception.message_dict)
        self.assertEqual(message, cm.exception.message_dict[field_name])
