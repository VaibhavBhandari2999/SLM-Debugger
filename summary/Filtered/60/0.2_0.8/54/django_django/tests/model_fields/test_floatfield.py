from django.db import transaction
from django.test import TestCase

from .models import FloatModel


class TestFloatField(TestCase):

    def test_float_validates_object(self):
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
        
        This function tests various invalid input types and values to ensure that the 'size' field in the FloatModel raises the appropriate exceptions with the correct error messages.
        
        Parameters:
        - exception (type): The expected exception type to be raised.
        - value (various): The invalid value to be tested.
        
        Returns:
        - None: The function asserts that the correct exception is raised with the expected error message for each test case
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
