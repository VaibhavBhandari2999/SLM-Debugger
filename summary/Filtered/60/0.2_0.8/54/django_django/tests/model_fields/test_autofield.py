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
        Test whether a given field is a subclass of models.AutoField.
        
        This function iterates over a list of field types (BigAutoField and SmallAutoField) and checks if each field is a subclass of models.AutoField. For each field, a sub-test is run to verify the subclass relationship.
        
        Parameters:
        None
        
        Returns:
        None
        
        Keywords:
        field: A field type from the Django models module (e.g., models.BigAutoField, models.SmallAutoField).
        
        Example:
        >>> test
        """

        for field in (models.BigAutoField, models.SmallAutoField):
            with self.subTest(field.__name__):
                self.assertTrue(issubclass(field, models.AutoField))
