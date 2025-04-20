from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from .models import DataModel


class BinaryFieldTests(TestCase):
    binary_data = b'\x00\x46\xFE'

    def test_set_and_retrieve(self):
        """
        Test the set and retrieve functionality of the DataModel.
        
        This test function checks the ability of the DataModel to correctly set and retrieve binary data, bytearray, and memoryview objects. It also verifies that the data remains consistent after saving and resaving, and that the default value for short_data is correctly set.
        
        Parameters:
        - self: The test case instance (unittest.TestCase).
        
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
        Tests the 'editable' attribute of the BinaryField model field.
        
        This function checks the 'editable' attribute of the BinaryField model field. It verifies that the attribute is correctly set to False by default and can be explicitly set to True or False.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Attributes:
        - field: An instance of the BinaryField model field.
        
        Test Cases:
        - Default value of 'editable' is False.
        - 'editable' can be set to True
        """

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
        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=bytearray(self.binary_data)), [dm])

    def test_filter_memoryview(self):
        """
        Tests the filtering functionality of DataModel objects based on memoryview of binary data.
        
        Parameters:
        self (unittest.TestCase): The current test case.
        
        Returns:
        None: This function asserts the expected behavior of filtering DataModel objects using memoryview of binary data.
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=memoryview(self.binary_data)), [dm])
        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=memoryview(self.binary_data)), [dm])
