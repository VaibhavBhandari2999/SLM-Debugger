from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from .models import DataModel


class BinaryFieldTests(TestCase):
    binary_data = b'\x00\x46\xFE'

    def test_set_and_retrieve(self):
        """
        Tests the functionality of setting and retrieving binary data in a DataModel object.
        
        This function tests the ability to set and retrieve binary data, including byte arrays and memoryviews, in a DataModel object. It also verifies that the data remains consistent after saving and resaving the object. Additionally, it checks the default value for a short_data field.
        
        Parameters:
        - self: The test case instance (unittest.TestCase).
        
        Key Parameters:
        - data_set: A tuple containing different types of binary data to be tested
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
        Tests the filter method of the DataModel queryset.
        
        This function creates a DataModel instance with a specific binary data and another instance with a different binary data. It then filters the DataModel queryset using the 'data' field with the specific binary data and asserts that the result is a sequence containing only the first instance.
        
        Parameters:
        self: The current test case instance.
        
        Returns:
        None
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=self.binary_data), [dm])

    def test_filter_bytearray(self):
        """
        Tests the filter method for DataModel objects with a bytearray parameter.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - Creates a DataModel instance with a given bytearray `self.binary_data`.
        - Creates another DataModel instance with a different bytearray `b'\xef\xbb\xbf'`.
        - Asserts that filtering DataModel objects with the given bytearray `self.binary_data` returns the expected instance.
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
        
        Key Points:
        - Creates a DataModel instance with a specific binary data.
        - Creates another DataModel instance with a different binary data.
        - Filters the DataModel objects using a memoryview of the initial binary data.
        - Asserts that the filtered result contains only the expected DataModel instance.
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=memoryview(self.binary_data)), [dm])
