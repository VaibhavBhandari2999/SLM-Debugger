from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from .models import DataModel


class BinaryFieldTests(TestCase):
    binary_data = b'\x00\x46\xFE'

    def test_set_and_retrieve(self):
        """
        Tests the functionality of setting and retrieving binary data in a DataModel object.
        
        This function tests the ability to set and retrieve binary data in a DataModel object. It uses three different types of binary data: a bytes object, a bytearray, and a memoryview. For each type of binary data, it performs the following steps:
        1. Creates a DataModel instance with the given binary data.
        2. Saves the instance to the database.
        3. Retrieves the instance from the database and checks if the
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
        Tests the 'editable' attribute of the BinaryField model.
        
        This function checks the 'editable' attribute of the BinaryField model. It verifies that the attribute is set correctly based on the provided arguments.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Checks:
        - When no 'editable' argument is provided, the 'editable' attribute is set to False.
        - When 'editable=True' is provided, the 'editable' attribute is set to True.
        - When 'editable=False
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
        """
        Tests the filtering functionality for DataModel objects based on a specific bytearray.
        
        Parameters:
        - self: The current test case object.
        
        Key Parameters:
        - binary_data: The bytearray to be used for filtering.
        
        Output:
        - Asserts that the query returns a sequence containing the expected DataModel object.
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=bytearray(self.binary_data)), [dm])

    def test_filter_memoryview(self):
        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=memoryview(self.binary_data)), [dm])
