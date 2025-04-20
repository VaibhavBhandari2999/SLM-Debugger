from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from .models import DataModel


class BinaryFieldTests(TestCase):
    binary_data = b'\x00\x46\xFE'

    def test_set_and_retrieve(self):
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
        """
        Tests the validation of a DataModel instance with data that exceeds the maximum allowed length.
        
        Args:
        self: The current test case instance.
        
        Returns:
        None. The function raises a ValidationError if the data length exceeds the maximum allowed length.
        
        Raises:
        ValidationError: If the length of the data exceeds the maximum allowed length.
        
        Key Parameters:
        - short_data (bytes): The binary data to be used in the DataModel instance. The data is repeated 4 times for testing.
        
        Keywords:
        """

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
        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=self.binary_data), [dm])

    def test_filter_bytearray(self):
        """
        Tests the `filter` method with a `bytearray` data type.
        
        This function creates a `DataModel` instance with a `bytearray` data and another instance with a different `bytearray` data. It then filters the `DataModel` objects using the `filter` method with the `bytearray` data and asserts that the returned sequence contains only the expected `DataModel` instance.
        
        Parameters:
        - No explicit parameters are required for this function.
        
        Returns:
        - None: This function
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=bytearray(self.binary_data)), [dm])

    def test_filter_memoryview(self):
        """
        Tests the filtering functionality of the DataModel model using a memoryview.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Creates a DataModel instance with a specified binary data.
        2. Creates another DataModel instance with a different binary data.
        3. Filters the DataModel objects using a memoryview of the initial binary data.
        4. Asserts that the filtered result contains only the initial DataModel instance.
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=memoryview(self.binary_data)), [dm])
