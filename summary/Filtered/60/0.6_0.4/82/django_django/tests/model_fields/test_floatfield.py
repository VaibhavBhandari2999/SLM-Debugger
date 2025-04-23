from django.db import transaction
from django.test import TestCase

from .models import FloatModel


class TestFloatField(TestCase):

    def test_float_validates_object(self):
        """
        Tests the validation of a float field in a model.
        
        This function checks the behavior of a float field in a model instance. It attempts to set the float field to both an unsaved and a saved object instance, and ensures that the field only accepts values compatible with a FloatField. The function uses a transaction to ensure that the database operations are atomic.
        
        Key Parameters:
        - `instance`: An instance of `FloatModel` with a float field `size`.
        
        Keywords:
        - `transaction.atomic()`:
        """

        instance = FloatModel(size=2.5)
        # Try setting float field to unsaved object
        instance.size = instance
        with transaction.atomic():
            with self.assertRaises(TypeError):
                instance.save()
        # Set value to valid and save
        instance.size = 2.5
        instance.save()
        self.assertTrue(instance.id)
        # Set field to object on saved instance
        instance.size = instance
        msg = (
            'Tried to update field model_fields.FloatModel.size with a model '
            'instance, %r. Use a value compatible with FloatField.'
        ) % instance
        with transaction.atomic():
            with self.assertRaisesMessage(TypeError, msg):
                instance.save()
        # Try setting field to object on retrieved object
        obj = FloatModel.objects.get(pk=instance.id)
        obj.size = obj
        with self.assertRaisesMessage(TypeError, msg):
            obj.save()

    def test_invalid_value(self):
        """
        Tests the validation of invalid input values for the 'size' field in the FloatModel.
        
        This function tests the 'size' field in the FloatModel to ensure it raises the appropriate exceptions for invalid input types and values. The function iterates over a list of test cases, each containing an expected exception type and a value to test. For each test case, it creates a sub-test to check if the specified exception is raised with the correct error message.
        
        Parameters:
        None
        
        Returns:
        None
        """

        tests = [
            (TypeError, ()),
            (TypeError, []),
            (TypeError, {}),
            (TypeError, set()),
            (TypeError, object()),
            (TypeError, complex()),
            (ValueError, 'non-numeric string'),
            (ValueError, b'non-numeric byte-string'),
        ]
        for exception, value in tests:
            with self.subTest(value):
                msg = "Field 'size' expected a number but got %r." % (value,)
                with self.assertRaisesMessage(exception, msg):
                    FloatModel.objects.create(size=value)
