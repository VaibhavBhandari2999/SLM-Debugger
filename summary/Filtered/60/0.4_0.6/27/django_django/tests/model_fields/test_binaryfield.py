from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from .models import DataModel


class BinaryFieldTests(TestCase):
    binary_data = b'\x00\x46\xFE'

    def test_set_and_retrieve(self):
        """
        Tests the functionality of setting and retrieving binary data in a DataModel.
        
        This function tests the ability to set and retrieve binary data of different types (bytes, bytearray, memoryview) in a DataModel. It also tests the behavior of resaving the model instance and the default value assignment for a field named 'short_data'.
        
        Parameters:
        - No external parameters are passed to this function. It uses instance variables and predefined data for testing.
        
        Key Steps:
        1. Defines a set of binary data types to
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
        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=self.binary_data), [dm])

    def test_filter_bytearray(self):
        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=bytearray(self.binary_data)), [dm])

    def test_filter_memoryview(self):
        """
        Tests the filtering functionality for DataModel objects based on memoryview of binary data.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - Creates a DataModel instance with specified binary data.
        - Creates another DataModel instance with a different binary data.
        - Filters DataModel objects using memoryview of the initial binary data.
        - Asserts that the filter returns the expected DataModel instance.
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=memoryview(self.binary_data)), [dm])
