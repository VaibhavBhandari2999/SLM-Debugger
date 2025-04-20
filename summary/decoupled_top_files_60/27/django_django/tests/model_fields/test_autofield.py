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
        Tests the isinstance method for the BigAutoField and SmallAutoField classes. Both fields are instances of the AutoField class. The function iterates over the specified field types, and for each, it checks if the field instance is an instance of AutoField using the isinstance method. The test is conducted within a subTest context to ensure clear and isolated testing of each field type.
        
        Parameters:
        None
        
        Returns:
        None
        """

        for field in (models.BigAutoField, models.SmallAutoField):
            with self.subTest(field.__name__):
                self.assertIsInstance(field(), models.AutoField)

    def test_issubclass_of_autofield(self):
        for field in (models.BigAutoField, models.SmallAutoField):
            with self.subTest(field.__name__):
                self.assertTrue(issubclass(field, models.AutoField))
            self.assertTrue(issubclass(field, models.AutoField))
