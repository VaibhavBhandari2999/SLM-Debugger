from django.core.exceptions import ValidationError


class ValidationAssertions:
    def assertFailsValidation(self, clean, failed_fields, **kwargs):
        with self.assertRaises(ValidationError) as cm:
            clean(**kwargs)
        self.assertEqual(sorted(failed_fields), sorted(cm.exception.message_dict))

    def assertFieldFailsValidationWithMessage(self, clean, field_name, message):
        """
        Asserts that a form field fails validation with a specific message.
        
        Parameters:
        clean (function): The form's clean method to be called.
        field_name (str): The name of the field to check for validation failure.
        message (str): The expected error message for the field.
        
        This function is used to verify that a form field fails validation and that the error message matches the expected message. It raises a ValidationError if the field does not fail validation or if the error message does not match
        """

        with self.assertRaises(ValidationError) as cm:
            clean()
        self.assertIn(field_name, cm.exception.message_dict)
        self.assertEqual(message, cm.exception.message_dict[field_name])
