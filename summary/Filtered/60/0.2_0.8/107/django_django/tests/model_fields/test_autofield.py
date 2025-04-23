from django.db import models
from django.test import SimpleTestCase

from .models import AutoModel, BigAutoModel, SmallAutoModel
from .test_integerfield import (
    BigIntegerFieldTests,
    IntegerFieldTests,
    SmallIntegerFieldTests,
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
        """
        Tests whether the given fields (BigAutoField and SmallAutoField) return an instance of AutoField when instantiated.
        
        Parameters:
        None
        
        Returns:
        None
        
        This function iterates over the specified field types (BigAutoField and SmallAutoField). For each field type, it creates an instance and checks if the instance is an instance of AutoField using the isinstance() function. The results of these checks are not explicitly returned or used; they are part of a series of subtests for detailed
        """

        for field in (models.BigAutoField, models.SmallAutoField):
            with self.subTest(field.__name__):
                self.assertIsInstance(field(), models.AutoField)

    def test_issubclass_of_autofield(self):
        """
        Test if a given field class is a subclass of models.AutoField.
        
        This function checks whether a provided field class is a subclass of models.AutoField. It supports both custom field classes and built-in field classes.
        
        Parameters:
        field (type): The field class to be tested.
        
        Returns:
        None: The function uses assertions to validate the input and does not return any value. It raises an AssertionError if the field is not a subclass of models.AutoField.
        
        Test Cases:
        - MyBigAutoField (custom class
        """

        class MyBigAutoField(models.BigAutoField):
            pass

        class MySmallAutoField(models.SmallAutoField):
            pass

        tests = [
            MyBigAutoField,
            MySmallAutoField,
            models.BigAutoField,
            models.SmallAutoField,
        ]
        for field in tests:
            with self.subTest(field.__name__):
                self.assertTrue(issubclass(field, models.AutoField))
