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
        Tests that a blank string is saved as NULL in the database.
        
        This function creates a new instance of the GenericIPAddress model with an empty string as the IP address. It then refreshes the object from the database to ensure that the IP address is saved as NULL. After that, it updates all instances of the GenericIPAddress model with an empty string and refreshes the object again to confirm that the IP address is still saved as NULL.
        
        Parameters:
        None
        
        Returns:
        None
        """

        o = GenericIPAddress.objects.create(ip='')
        o.refresh_from_db()
        self.assertIsNone(o.ip)
        GenericIPAddress.objects.update(ip='')
        o.refresh_from_db()
        self.assertIsNone(o.ip)

    def test_save_load(self):
        instance = GenericIPAddress.objects.create(ip='::1')
        loaded = GenericIPAddress.objects.get()
        self.assertEqual(loaded.ip, instance.ip)
