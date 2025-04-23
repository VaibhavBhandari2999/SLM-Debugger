from django.db import models
from django.test import SimpleTestCase

from .models import AutoModel, BigAutoModel, SmallAutoModel
from .test_integerfield import (
    BigIntegerFieldTests, IntegerFieldTests, SmallIntegerFieldTests,
)


class AutoFieldTests(IntegerFieldTests):
    model = AutoModel
    rel_db_type_class = models.IntegerField


class BigAutoFieldTests(BigIntegerFieldTests):
    model = BigAutoModel
    rel_db_type_class = models.BigIntegerField


class SmallAutoFieldTests(SmallIntegerFieldTests):
    model = SmallAutoModel
    rel_db_type_class = models.SmallIntegerField


class AutoFieldInheritanceTests(SimpleTestCase):

    def test_isinstance_of_autofield(self):
        for field in (models.BigAutoField, models.SmallAutoField):
            with self.subTest(field.__name__):
                self.assertIsInstance(field(), models.AutoField)

    def test_issubclass_of_autofield(self):
        """
        Tests whether the specified fields are subclasses of models.AutoField.
        
        This function iterates over a list of fields, which includes models.BigAutoField and models.SmallAutoField. For each field, it checks if the field is a subclass of models.AutoField using the issubclass function. The result of each check is verified using a subTest context manager to ensure that the test is run for each field individually.
        
        Parameters:
        None
        
        Returns:
        None
        """

        for field in (models.BigAutoField, models.SmallAutoField):
            with self.subTest(field.__name__):
                self.assertTrue(issubclass(field, models.AutoField))
