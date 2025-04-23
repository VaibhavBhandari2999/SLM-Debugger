from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from .models import DataModel


class BinaryFieldTests(TestCase):
    binary_data = b"\x00\x46\xFE"

    def test_set_and_retrieve(self):
        """
        Tests the functionality of setting and retrieving data in a DataModel object.
        
        This function tests the ability to set and retrieve different types of binary data (bytes, bytearray, memoryview) in a DataModel object. It also tests the behavior of saving and resaving the object, as well as the default value for a short_data field.
        
        Parameters:
        - None (The function uses instance variables and does not take any parameters).
        
        Key Steps:
        1. Defines a set of binary data types to test.
        2
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
        
        This function creates a DataModel instance with a specific binary data and another instance with a different binary data. It then filters the DataModel objects using a memoryview of the initial binary data and asserts that the filtered result contains only the expected DataModel instance.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Elements:
        - `binary_data`: The binary data used to create the first DataModel instance.
        - `memoryview`:
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b"\xef\xbb\xbf")
        self.assertSequenceEqual(
            DataModel.objects.filter(data=memoryview(self.binary_data)), [dm]
        )
