from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from .models import GenericIPAddress


class GenericIPAddressFieldTests(TestCase):

    def test_genericipaddressfield_formfield_protocol(self):
        """
        GenericIPAddressField with a specified protocol does not generate a
        formfield without a protocol.
        """
        model_field = models.GenericIPAddressField(protocol='IPv4')
        form_field = model_field.formfield()
        with self.assertRaises(ValidationError):
            form_field.clean('::1')
        model_field = models.GenericIPAddressField(protocol='IPv6')
        form_field = model_field.formfield()
        with self.assertRaises(ValidationError):
            form_field.clean('127.0.0.1')

    def test_null_value(self):
        """
        Null values should be resolved to None.
        """
        GenericIPAddress.objects.create()
        o = GenericIPAddress.objects.get()
        self.assertIsNone(o.ip)

    def test_blank_string_saved_as_null(self):
        """
        Tests the behavior of saving a blank string to a GenericIPAddress field.
        
        This function creates an instance of the GenericIPAddress model with an empty string as the IP address. It then refreshes the object from the database and checks if the IP address is set to None, indicating that an empty string is saved as NULL in the database. The function also updates the IP address of all instances of the model to an empty string and refreshes an instance to verify the same behavior.
        
        Key Parameters:
        - None
        """

        o = GenericIPAddress.objects.create(ip='')
        o.refresh_from_db()
        self.assertIsNone(o.ip)
        GenericIPAddress.objects.update(ip='')
        o.refresh_from_db()
        self.assertIsNone(o.ip)

    def test_save_load(self):
        """
        Tests the save and load functionality of the GenericIPAddress model.
        
        This function creates an instance of the GenericIPAddress model with an IP address '::1' and saves it. It then retrieves the saved instance and checks if the IP address is correctly loaded.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Attributes:
        - instance: An instance of the GenericIPAddress model with the IP address '::1'.
        - loaded: The instance of the GenericIPAddress model retrieved from the database.
        
        Assertions:
        -
        """

        instance = GenericIPAddress.objects.create(ip='::1')
        loaded = GenericIPAddress.objects.get()
        self.assertEqual(loaded.ip, instance.ip)
