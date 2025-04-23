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
        for field in (models.BigAutoField, models.SmallAutoField):
            with self.subTest(field.__name__):
                self.assertIsInstance(field(), models.AutoField)

    def test_issubclass_of_autofield(self):
        """
        Tests if a given field is a subclass of models.AutoField.
        
        This function iterates over a list of fields, which includes models.BigAutoField and models.SmallAutoField, and checks if each field is a subclass of models.AutoField. The test is performed using a subtest for each field to ensure clear and isolated testing.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If any of the fields is not a subclass of models.AutoField.
        
        Example:
        >>> test_issub
        """

        for field in (models.BigAutoField, models.SmallAutoField):
            with self.subTest(field.__name__):
                self.assertTrue(issubclass(field, models.AutoField))
