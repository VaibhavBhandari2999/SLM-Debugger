from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from .models import DataModel


class BinaryFieldTests(TestCase):
    binary_data = b"\x00\x46\xFE"

    def test_set_and_retrieve(self):
        """
        Tests the functionality of setting and retrieving data in a DataModel.
        
        This function tests the ability of a DataModel to correctly set and retrieve binary data in various formats (bytes, bytearray, memoryview). It also verifies that the data remains consistent after saving and resaving the model instance. Additionally, it checks the default value for a short_data field.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Steps:
        1. Define a set of binary data in different formats.
        2. Iterate through each
        """

        data_set = (
            self.binary_data,
            bytearray(self.binary_data),
            memoryview(self.binary_data),
        )
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
                self.assertEqual(bytes(dm.short_data), b"\x08")

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
        
        Purpose: Test the filtering functionality for a DataModel object that contains binary data.
        
        Parameters:
        - self: The test case object that provides access to methods and attributes for testing.
        
        Returns:
        - None: This function is a test case and does not return a value. It asserts that the filter operation on DataModel objects returns the expected result.
        
        Description:
        This function creates a DataModel object with specific binary data and another object with a different binary data. It then filters the
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b"\xef\xbb\xbf")
        self.assertSequenceEqual(DataModel.objects.filter(data=self.binary_data), [dm])

    def test_filter_bytearray(self):
        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b"\xef\xbb\xbf")
        self.assertSequenceEqual(
            DataModel.objects.filter(data=bytearray(self.binary_data)), [dm]
        )

    def test_filter_memoryview(self):
        """
        Tests the filtering functionality of the DataModel model using a memoryview.
        
        This test checks if the DataModel objects can be correctly filtered using a memoryview of binary data. It creates a DataModel instance with specific binary data and another with different binary data. Then, it filters the DataModel objects using a memoryview of the initial binary data and asserts that only the expected DataModel instance is returned.
        
        Parameters:
        - self.binary_data (bytes): The binary data used to create and filter the DataModel
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b"\xef\xbb\xbf")
        self.assertSequenceEqual(
            DataModel.objects.filter(data=memoryview(self.binary_data)), [dm]
        )
