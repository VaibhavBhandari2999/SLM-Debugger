from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from .models import DataModel


class BinaryFieldTests(TestCase):
    binary_data = b'\x00\x46\xFE'

    def test_set_and_retrieve(self):
        """
        Tests the functionality of setting and retrieving binary data in a DataModel object.
        
        This function tests the ability of the DataModel to correctly store and retrieve binary data. It performs the following steps:
        1. Iterates over a set of binary data types: bytes, bytearray, and memoryview.
        2. For each data type, it creates a DataModel instance with the binary data.
        3. Saves the DataModel instance and retrieves it to check if the data is correctly stored.
        4. Resaves the
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
        field = models.BinaryField()
        self.assertIs(field.editable, False)
        field = models.BinaryField(editable=True)
        self.assertIs(field.editable, True)
        field = models.BinaryField(editable=False)
        self.assertIs(field.editable, False)

    def test_filter(self):
        """
        Function: test_filter
        ---------------------
        Tests the filtering functionality of the DataModel model.
        
        Parameters:
        self: The current test case instance.
        
        Returns:
        None: This function asserts the expected behavior of the filter method on the DataModel model.
        
        Key Points:
        - Creates a DataModel instance with a specific binary data.
        - Creates another DataModel instance with a different binary data.
        - Uses the filter method to retrieve DataModel instances with the specified binary data.
        - Asserts that the filter method
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=self.binary_data), [dm])

    def test_filter_bytearray(self):
        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=bytearray(self.binary_data)), [dm])

    def test_filter_memoryview(self):
        """
        Tests the filtering functionality of DataModel objects based on memoryview of binary data.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - Creates a DataModel instance with specified binary data.
        - Creates another DataModel instance with a different binary data.
        - Filters DataModel objects using memoryview of the original binary data.
        - Asserts that the filtered result contains only the expected DataModel instance.
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=memoryview(self.binary_data)), [dm])
