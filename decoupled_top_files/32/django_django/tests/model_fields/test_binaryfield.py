from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from .models import DataModel


class BinaryFieldTests(TestCase):
    binary_data = b'\x00\x46\xFE'

    def test_set_and_retrieve(self):
        """
        Tests setting and retrieving binary data using different data types (bytes, bytearray, memoryview). The function creates a DataModel instance, saves it, retrieves it, and verifies that the data is correctly stored and retrieved. It also tests updating the model and checking the default value for short_data.
        
        Important Functions:
        - `DataModel`: Used to create and manipulate model instances.
        - `save()`: Saves the model instance to the database.
        - `objects.get()`: Retrieves a
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
        """
        Test the maximum length validation for a DataModel instance.
        
        This function creates a DataModel instance with `short_data` set to four times the binary data provided. It then attempts to validate the model using `full_clean()`. If the `short_data` exceeds the allowed maximum length, a `ValidationError` is raised.
        
        Args:
        None (the test case is designed to be called without any arguments).
        
        Returns:
        None (the function asserts that a `ValidationError` is
        """

        dm = DataModel(short_data=self.binary_data * 4)
        with self.assertRaises(ValidationError):
            dm.full_clean()

    def test_editable(self):
        """
        Tests the `editable` attribute of the `BinaryField` model.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `models.BinaryField`: Creates a binary field with specified attributes.
        - `self.assertIs`: Compares two values and asserts that they are equal.
        
        Attributes Affected:
        - `field.editable`: Indicates whether the field is editable or not.
        """

        field = models.BinaryField()
        self.assertIs(field.editable, False)
        field = models.BinaryField(editable=True)
        self.assertIs(field.editable, True)
        field = models.BinaryField(editable=False)
        self.assertIs(field.editable, False)

    def test_filter(self):
        """
        Tests the filtering functionality of the DataModel model using the `filter` method. Creates two instances of DataModel with different binary data, then filters the queryset to find instances matching a specific binary data value, asserting that only one instance is returned.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `DataModel.objects.create()`: Creates new instances of the DataModel model.
        - `filter()`: Filters the queryset based on the specified condition.
        -
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=self.binary_data), [dm])

    def test_filter_bytearray(self):
        """
        Tests filtering of DataModel objects based on bytearray data.
        
        This function creates two DataModel instances with different data values:
        - One with `self.binary_data` converted to a bytearray
        - One with the byte order mark (BOM) `b'\xef\xbb\xbf'`
        
        It then filters the DataModel objects using the `filter` method with the `data` field set to the bytearray representation of `self.binary_data`.
        
        Args:
        None
        
        Returns:
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=bytearray(self.binary_data)), [dm])

    def test_filter_memoryview(self):
        """
        Tests filtering of DataModel objects using a memoryview.
        Creates two DataModel instances with different data.
        Filters DataModel objects where the data matches the given memoryview of binary data and asserts that only one instance is returned.
        """

        dm = DataModel.objects.create(data=self.binary_data)
        DataModel.objects.create(data=b'\xef\xbb\xbf')
        self.assertSequenceEqual(DataModel.objects.filter(data=memoryview(self.binary_data)), [dm])
