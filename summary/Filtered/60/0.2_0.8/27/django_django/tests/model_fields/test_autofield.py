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
        Tests the isinstance method for the BigAutoField and SmallAutoField classes, ensuring they are instances of AutoField.
        
        Parameters:
        None
        
        Returns:
        None
        
        This function iterates over the BigAutoField and SmallAutoField classes, and for each, it checks if an instance of the field is an instance of AutoField using the isinstance method. It uses a subTest context manager to provide detailed test results for each field.
        """

        for field in (models.BigAutoField, models.SmallAutoField):
            with self.subTest(field.__name__):
                self.assertIsInstance(field(), models.AutoField)

    def test_issubclass_of_autofield(self):
        for field in (models.BigAutoField, models.SmallAutoField):
            with self.subTest(field.__name__):
                self.assertTrue(issubclass(field, models.AutoField))
):
            with self.subTest(field.__name__):
                self.assertTrue(issubclass(field, models.AutoField))
