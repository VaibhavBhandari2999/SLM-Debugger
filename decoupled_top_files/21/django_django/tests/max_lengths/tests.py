import unittest

from django.test import TestCase

from .models import PersonWithCustomMaxLengths, PersonWithDefaultMaxLengths


class MaxLengthArgumentsTests(unittest.TestCase):

    def verify_max_length(self, model, field, length):
        self.assertEqual(model._meta.get_field(field).max_length, length)

    def test_default_max_lengths(self):
        """
        Tests the maximum length constraints for various fields in the PersonWithDefaultMaxLengths model.
        
        This function verifies that the specified fields in the PersonWithDefaultMaxLengths model adhere to their respective maximum length constraints using the `verify_max_length` function.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - verify_max_length: Used to check if the field values do not exceed their defined maximum lengths.
        
        Fields Tested:
        - email (max length: 25
        """

        self.verify_max_length(PersonWithDefaultMaxLengths, 'email', 254)
        self.verify_max_length(PersonWithDefaultMaxLengths, 'vcard', 100)
        self.verify_max_length(PersonWithDefaultMaxLengths, 'homepage', 200)
        self.verify_max_length(PersonWithDefaultMaxLengths, 'avatar', 100)

    def test_custom_max_lengths(self):
        """
        Tests the maximum length constraints for specific fields in the PersonWithCustomMaxLengths model.
        
        This function verifies that the maximum length constraints are correctly applied to the 'email', 'vcard', 'homepage', and 'avatar' fields of the PersonWithCustomMaxLengths model using the verify_max_length function.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - verify_max_length: Function used to check the maximum length of specified fields in the PersonWithCustomMaxLengths
        """

        self.verify_max_length(PersonWithCustomMaxLengths, 'email', 250)
        self.verify_max_length(PersonWithCustomMaxLengths, 'vcard', 250)
        self.verify_max_length(PersonWithCustomMaxLengths, 'homepage', 250)
        self.verify_max_length(PersonWithCustomMaxLengths, 'avatar', 250)


class MaxLengthORMTests(TestCase):

    def test_custom_max_lengths(self):
        """
        Tests custom maximum lengths for various fields in the PersonWithCustomMaxLengths model.
        
        This function creates instances of the PersonWithCustomMaxLengths model with values exceeding the default maximum lengths for specific fields: 'email', 'vcard', 'homepage', and 'avatar'. It then verifies that the values are correctly set to the maximum allowed length.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `PersonWithCustomMaxLengths.objects.create()`: Creates a new
        """

        args = {
            "email": "someone@example.com",
            "vcard": "vcard",
            "homepage": "http://example.com/",
            "avatar": "me.jpg"
        }

        for field in ("email", "vcard", "homepage", "avatar"):
            new_args = args.copy()
            new_args[field] = "X" * 250  # a value longer than any of the default fields could hold.
            p = PersonWithCustomMaxLengths.objects.create(**new_args)
            self.assertEqual(getattr(p, field), ("X" * 250))
