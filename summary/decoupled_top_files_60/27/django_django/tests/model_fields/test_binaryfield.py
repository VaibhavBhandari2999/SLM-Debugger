from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from .models import DataModel


class BinaryFieldTests(TestCase):
    binary_data = b'\x00\x46\xFE'

    def test_set_and_retrieve(self):
        """
        Test the set and retrieve functionality of the DataModel class.
        
        This test function checks the ability of the DataModel class to correctly set and retrieve binary data, bytearray, and memoryview objects. It also verifies that the data remains consistent after saving and resaving, and that the default value for short_data is correctly set.
        
        Parameters:
        - self: The current test case instance.
        
        Key Steps:
        1. Define a set of data types to test: binary data, bytearray, and memoryview.
        2.
        """

        data_set = (self.binary_data, bytearray(self.binary_data), memoryview(self.binary_data))
        for bdata in data_set:
            with self.subTest(data=repr(bdata)):
                dm = DataModel(data=bdata)
                dm.save()
                dm = DataModel.objects.get(pk=dm.pk)
                self.assertEqual(bytes(dm.data), bytes(bdata))
                # Resave (=update)
                dm.save()
                dm = DataModel.objects.get(pk=dm.pk)
                self.assertEqual(bytes(dm.data), bytes(bdata))
                # Test default value
                self.assertEqual(bytes(dm.short_data), b'\x08')

    def test_max_length(self):
        dm = DataModel(short_data=self.binary_data * 4)
        with self.assertRaises(ValidationError):
            dm.full_clean()

    def test_editable(self):
        """
        Tests the `editable` attribute of the `BinaryField` model field.
        
        This function checks the `editable` attribute of the `BinaryField` model field. It verifies that the attribute is set correctly based on the provided arguments. The `editable` attribute determines whether the field can be edited in the admin interface.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The `editable` attribute is set to `False` by default.
        - The `editable` attribute can be explicitly
        """

        field = models.BinaryField()
        self.assertIs(field.editable, False)
        field = models.BinaryField(editable=True)
        self.assertIs(field.editable, True)
        field = models.BinaryField(editable=False)
        self.assertIs(field.editable, False)

    def test_filter(self):
        """
        Function: test_filter
        
        This function tests the filtering functionality of the DataModel model based on binary data.
        
        Parameters:
        - self: The test case object (unittest.TestCase).
        
        Returns:
        - None: This function asserts the expected behavior of the filter method and does not return any value.
        
        Key Points:
        - A DataModel instance is created with a specific binary data.
        - Another DataModel instance is created with a different binary data.
        - The function asserts that filtering the DataModel objects with the specific binary
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=self.binary_data), [dm])

    def test_filter_bytearray(self):
        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=bytearray(self.binary_data)), [dm])

    def test_filter_memoryview(self):
        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=memoryview(self.binary_data)), [dm])
  self.assertSequenceEqual(DataModel.objects.filter(data=memoryview(self.binary_data)), [dm])
