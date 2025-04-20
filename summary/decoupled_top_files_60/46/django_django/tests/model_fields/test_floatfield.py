from django.db import transaction
from django.test import TestCase

from .models import FloatModel


class TestFloatField(TestCase):

    def test_float_validates_object(self):
        """
        Tests the validation of a float field in a model.
        
        This function tests the behavior of a float field in a model by setting the field to different types of values and ensuring that the appropriate exceptions are raised when invalid types are used.
        
        Key Parameters:
        - `instance`: An instance of `FloatModel` with a `size` field set to a float value.
        
        Keywords:
        - `transaction.atomic()`: Ensures that the database transaction is managed properly.
        - `self.assertRaises(TypeError)`: Used to assert
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
        
        This function tests various types of invalid input values for the 'size' field in the FloatModel. It expects a number but receives different types of non-numeric values. The function raises specific exceptions for each type of invalid input and includes a custom error message.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: If the input value is of a type that is not a number.
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
