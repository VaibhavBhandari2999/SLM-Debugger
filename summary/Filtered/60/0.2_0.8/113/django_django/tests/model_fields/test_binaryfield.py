from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from .models import DataModel


class BinaryFieldTests(TestCase):
    binary_data = b"\x00\x46\xFE"

    def test_set_and_retrieve(self):
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
        """
        Test the maximum length validation for a DataModel object.
        
        This function creates a DataModel instance with 'short_data' set to a binary data repeated four times. It then attempts to validate the instance using full_clean(). If the length of 'short_data' exceeds the allowed maximum, a ValidationError is expected to be raised.
        
        Parameters:
        self: The current test case instance.
        
        Returns:
        None: The function asserts that a ValidationError is raised during full_clean(). If no exception is raised, the test
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
        """
        Tests the filter method of the DataModel model.
        
        This function creates a DataModel object with specified binary data and another object with a different binary data. It then filters the DataModel objects using the specified binary data and asserts that the result is a sequence containing only the first created DataModel object.
        
        Parameters:
        self: The current test case instance.
        
        Returns:
        None
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b"\xef\xbb\xbf")
        self.assertSequenceEqual(DataModel.objects.filter(data=self.binary_data), [dm])

    def test_filter_bytearray(self):
        """
        Tests filtering a DataModel instance by a specific bytearray.
        
        This function creates a DataModel instance with a given bytearray `self.binary_data` and another instance with a different bytearray. It then filters the DataModel objects to find those matching the specified bytearray and asserts that the result contains only the expected instance.
        
        Parameters:
        self (unittest.TestCase): The test case instance.
        
        Returns:
        None: This function asserts the result and does not return any value.
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b"\xef\xbb\xbf")
        self.assertSequenceEqual(
            DataModel.objects.filter(data=bytearray(self.binary_data)), [dm]
        )

    def test_filter_memoryview(self):
        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b"\xef\xbb\xbf")
        self.assertSequenceEqual(
            DataModel.objects.filter(data=memoryview(self.binary_data)), [dm]
        )
