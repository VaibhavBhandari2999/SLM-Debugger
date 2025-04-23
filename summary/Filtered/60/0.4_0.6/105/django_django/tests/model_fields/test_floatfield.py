from django.db import transaction
from django.test import TestCase

from .models import FloatModel


class TestFloatField(TestCase):
    def test_float_validates_object(self):
        """
        Tests the validation of a float field in a model.
        
        This function tests the behavior of a float field in a model instance. It creates an instance of `FloatModel` with a float value and then attempts to set the float field to different types of values, including an unsaved object, a valid float, and a saved object. The function uses a transaction to ensure that the model instance is not saved if validation fails. The test checks that setting the field to an unsaved object or a saved
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
            "Tried to update field model_fields.FloatModel.size with a model "
            "instance, %r. Use a value compatible with FloatField."
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
        
        This function tests various invalid input types and values for the 'size' field in the FloatModel. It expects a number but receives different types of non-numeric values. The function iterates through a list of test cases, each containing an expected exception type and a value to test. For each test case, it creates a sub-test to validate that the incorrect value raises the expected exception with an appropriate error message
        """

        tests = [
            (TypeError, ()),
            (TypeError, []),
            (TypeError, {}),
            (TypeError, set()),
            (TypeError, object()),
            (TypeError, complex()),
            (ValueError, "non-numeric string"),
            (ValueError, b"non-numeric byte-string"),
        ]
        for exception, value in tests:
            with self.subTest(value):
                msg = "Field 'size' expected a number but got %r." % (value,)
                with self.assertRaisesMessage(exception, msg):
                    FloatModel.objects.create(size=value)
