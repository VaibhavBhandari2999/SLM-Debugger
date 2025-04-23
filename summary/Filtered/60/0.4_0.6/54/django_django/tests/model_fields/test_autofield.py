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
        Tests whether the given field instances are instances of models.AutoField.
        
        This function iterates over a list of field classes (BigAutoField and SmallAutoField) and checks if each instance of these fields is an instance of models.AutoField. Each check is performed within a sub-test for better isolation and readability.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If any of the field instances is not an instance of models.AutoField.
        """

        for field in (models.BigAutoField, models.SmallAutoField):
            with self.subTest(field.__name__):
                self.assertIsInstance(field(), models.AutoField)

    def test_issubclass_of_autofield(self):
        """
        Tests whether the specified fields are subclasses of models.AutoField.
        
        This function iterates over a list of field types, which includes models.BigAutoField and models.SmallAutoField. For each field type, it checks if the field is a subclass of models.AutoField using the issubclass function. The result of each check is verified using a subTest context manager to ensure that each field correctly inherits from models.AutoField.
        
        Parameters:
        None
        
        Returns:
        None
        """

        for field in (models.BigAutoField, models.SmallAutoField):
            with self.subTest(field.__name__):
                self.assertTrue(issubclass(field, models.AutoField))
