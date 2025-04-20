from django.db import transaction
from django.test import TestCase

from .models import FloatModel


class TestFloatField(TestCase):

    def test_float_validates_object(self):
        """
        Tests the validation of a float field in a model.
        
        This function tests the behavior of a float field in a model when an object is assigned to it. It checks the following scenarios:
        1. Setting a float field on an unsaved object with another object instance.
        2. Setting a valid float value and saving the object.
        3. Setting a float field on a saved object with another object instance.
        4. Setting a float field on a retrieved object with another object instance.
        
        Key Parameters:
        - `
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
