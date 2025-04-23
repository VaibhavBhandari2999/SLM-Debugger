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
        
        Parameters:
        self: The current test case instance.
        
        Returns:
        None. This function asserts that the filter method correctly returns the expected DataModel object.
        
        Key Points:
        - `dm`: A DataModel instance created with specific binary data.
        - `self.binary_data`: The binary data used to create the `dm` instance.
        - The function asserts that filtering the DataModel queryset with `self.binary_data` returns the expected instance.
        - Additional Data
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b"\xef\xbb\xbf")
        self.assertSequenceEqual(DataModel.objects.filter(data=self.binary_data), [dm])

    def test_filter_bytearray(self):
        """
        Tests the filtering of DataModel objects based on a specific bytearray value.
        
        Parameters:
        self (unittest.TestCase): The test case instance.
        
        Returns:
        None: This function asserts the correctness of the filter operation and does not return any value.
        
        Key Parameters:
        - `self.binary_data`: A bytearray object used for testing the filter query.
        
        Key Behavior:
        - Creates a DataModel instance with the provided `binary_data`.
        - Creates another DataModel instance with a specific bytearray value.
        -
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
