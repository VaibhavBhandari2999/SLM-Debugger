from django.core.exceptions import ValidationError


class ValidationAssertions:
    def assertFailsValidation(self, clean, failed_fields, **kwargs):
        """
        Asserts that the provided `clean` function fails validation with the specified `failed_fields`.
        
        Parameters:
        clean (function): The clean function to test.
        failed_fields (list): A list of field names that are expected to fail validation.
        
        Keyword Arguments:
        **kwargs: Additional keyword arguments to pass to the `clean` function.
        
        Raises:
        ValidationError: If the `clean` function does not raise a ValidationError or if the failed fields do not match the expected fields.
        
        Returns:
        None
        """

        with self.assertRaises(ValidationError) as cm:
            clean(**kwargs)
        self.assertEqual(sorted(failed_fields), sorted(cm.exception.message_dict))

    def assertFieldFailsValidationWithMessage(self, clean, field_name, message):
        with self.assertRaises(ValidationError) as cm:
            clean()
        self.assertIn(field_name, cm.exception.message_dict)
        self.assertEqual(message, cm.exception.message_dict[field_name])
