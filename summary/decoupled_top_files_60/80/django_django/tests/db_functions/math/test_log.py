import math
from decimal import Decimal

from django.db.models.functions import Log
from django.test import TestCase

from ..models import DecimalModel, FloatModel, IntegerModel


class LogTests(TestCase):

    def test_null(self):
        """
        Tests the behavior of the Log function when applied to a null value.
        
        This function creates an instance of IntegerModel with a 'big' field set to 100. It then annotates the first instance of IntegerModel with two Log functions: 'null_log_small' and 'null_log_normal'. The 'null_log_small' function takes the 'small' field and divides it by the 'normal' field, while 'null_log_normal' takes the 'normal' field and divides it by
        """

        IntegerModel.objects.create(big=100)
        obj = IntegerModel.objects.annotate(
            null_log_small=Log('small', 'normal'),
            null_log_normal=Log('normal', 'big'),
        ).first()
        self.assertIsNone(obj.null_log_small)
        self.assertIsNone(obj.null_log_normal)

    def test_decimal(self):
        DecimalModel.objects.create(n1=Decimal('12.9'), n2=Decimal('3.6'))
        obj = DecimalModel.objects.annotate(n_log=Log('n1', 'n2')).first()
        self.assertIsInstance(obj.n_log, Decimal)
        self.assertAlmostEqual(obj.n_log, Decimal(math.log(obj.n2, obj.n1)))

    def test_float(self):
        """
        Tests the Log function for FloatModel objects.
        
        This function creates a FloatModel instance with predefined float values for f1 and f2. It then annotates the query with a Log function that calculates the logarithm of f2 with base f1. The test checks if the annotated field f_log is of type float and if its value is approximately equal to the expected result, which is the logarithm of f2 with base f1.
        
        Key Parameters:
        - None
        
        Returns:
        - None
        
        Assertions
        """

        FloatModel.objects.create(f1=2.0, f2=4.0)
        obj = FloatModel.objects.annotate(f_log=Log('f1', 'f2')).first()
        self.assertIsInstance(obj.f_log, float)
        self.assertAlmostEqual(obj.f_log, math.log(obj.f2, obj.f1))

    def test_integer(self):
        """
        Tests the logarithmic calculation functionality for different integer fields in a model.
        
        This function creates an instance of the IntegerModel with specified integer values for 'small', 'normal', and 'big' fields. It then annotates the query set with logarithmic values of these fields relative to each other using the Log function. The function asserts that the annotated logarithmic values are of type float and checks if they match the expected logarithmic calculations.
        
        Key Parameters:
        - None (The function uses model instances and database
        """

        IntegerModel.objects.create(small=4, normal=8, big=2)
        obj = IntegerModel.objects.annotate(
            small_log=Log('small', 'big'),
            normal_log=Log('normal', 'big'),
            big_log=Log('big', 'big'),
        ).first()
        self.assertIsInstance(obj.small_log, float)
        self.assertIsInstance(obj.normal_log, float)
        self.assertIsInstance(obj.big_log, float)
        self.assertAlmostEqual(obj.small_log, math.log(obj.big, obj.small))
        self.assertAlmostEqual(obj.normal_log, math.log(obj.big, obj.normal))
        self.assertAlmostEqual(obj.big_log, math.log(obj.big, obj.big))
