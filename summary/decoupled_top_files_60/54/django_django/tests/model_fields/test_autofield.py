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
        Tests the isinstance method for the BigAutoField and SmallAutoField classes. Both fields are expected to be instances of the AutoField class. The function iterates through the provided field types, and for each, it checks if an instance of the field is an instance of AutoField. The test is conducted within a subTest context to ensure that each field type is evaluated independently.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If any of the fields (BigAutoField
        """

        for field in (models.BigAutoField, models.SmallAutoField):
            with self.subTest(field.__name__):
                self.assertIsInstance(field(), models.AutoField)

    def test_issubclass_of_autofield(self):
        for field in (models.BigAutoField, models.SmallAutoField):
            with self.subTest(field.__name__):
                self.assertTrue(issubclass(field, models.AutoField))
models.AutoField))
