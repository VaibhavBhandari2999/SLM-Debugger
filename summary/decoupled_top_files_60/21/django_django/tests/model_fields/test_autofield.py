from django.db import models
from django.test import SimpleTestCase

from .models import AutoModel, BigAutoModel, SmallAutoModel
from .test_integerfield import (
    BigIntegerFieldTests, IntegerFieldTests, SmallIntegerFieldTests,
)


class AutoFieldTests(IntegerFieldTests):
    model = AutoModel


class BigAutoFieldTests(BigIntegerFieldTests):
    model = BigAutoModel


class SmallAutoFieldTests(SmallIntegerFieldTests):
    model = SmallAutoModel


class AutoFieldInheritanceTests(SimpleTestCase):

    def test_isinstance_of_autofield(self):
        """
        Test the isinstance method for AutoField and its subclasses (BigAutoField and SmallAutoField).
        
        This function checks if instances of BigAutoField and SmallAutoField are instances of AutoField.
        
        Parameters:
        None
        
        Returns:
        None
        
        Usage:
        This function is typically used in a testing context to ensure that the field types are correctly subclassing AutoField.
        """

        for field in (models.BigAutoField, models.SmallAutoField):
            with self.subTest(field.__name__):
                self.assertIsInstance(field(), models.AutoField)

    def test_issubclass_of_autofield(self):
        """
        Tests whether the specified fields (BigAutoField and SmallAutoField) are subclasses of AutoField.
        
        This function iterates over the provided fields and checks if each one is a subclass of AutoField using the issubclass function. It runs a subtest for each field to ensure individual verification.
        
        Parameters:
        None
        
        Returns:
        None
        
        Keywords:
        field: The field types to be tested, specifically BigAutoField and SmallAutoField.
        subTest: Used to run individual tests for each
        """

        for field in (models.BigAutoField, models.SmallAutoField):
            with self.subTest(field.__name__):
                self.assertTrue(issubclass(field, models.AutoField))
