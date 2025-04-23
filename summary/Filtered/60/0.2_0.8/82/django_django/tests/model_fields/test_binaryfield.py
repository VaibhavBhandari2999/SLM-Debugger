from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from .models import DataModel


class BinaryFieldTests(TestCase):
    binary_data = b'\x00\x46\xFE'

    def test_set_and_retrieve(self):
        """
        Tests the functionality of setting and retrieving binary data in a DataModel.
        
        This function tests the ability of the DataModel to correctly store and retrieve binary data. It uses three different types of binary data representations: a bytes object, a bytearray, and a memoryview. For each type of binary data, the function performs the following steps:
        1. Creates a DataModel instance with the given binary data.
        2. Saves the DataModel instance to the database.
        3. Retrieves the DataModel instance from the
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
        
        This function checks the 'editable' attribute of the BinaryField model field.
        It tests three scenarios:
        1. Default value of 'editable' is False.
        2. 'editable' is set to True.
        3. 'editable' is set to False.
        
        Parameters:
        None
        
        Returns:
        None
        
        Attributes Tested:
        field.editable (bool): Indicates whether the field is editable.
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
        Tests the filtering functionality for DataModel objects based on memoryview of binary data.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - Creates a DataModel instance with specified binary data.
        - Creates another DataModel instance with a different binary data.
        - Filters DataModel objects using a memoryview of the initial binary data.
        - Asserts that the filter returns the expected DataModel instance.
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=memoryview(self.binary_data)), [dm])
