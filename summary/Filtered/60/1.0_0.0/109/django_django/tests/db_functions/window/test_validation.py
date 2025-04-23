from django.db.models.functions import Lag, Lead, NthValue, Ntile
from django.test import SimpleTestCase


class ValidationTests(SimpleTestCase):
    def test_nth_negative_nth_value(self):
        msg = "NthValue requires a positive integer as for nth"
        with self.assertRaisesMessage(ValueError, msg):
            NthValue(expression="salary", nth=-1)

    def test_nth_null_expression(self):
        """
        Test the NthValue function with a null source expression.
        
        Args:
        expression (Expression): The source expression for the NthValue function.
        
        Raises:
        ValueError: If the source expression is null. The error message indicates that the NthValue function requires a non-null source expression.
        
        Example:
        >>> NthValue(expression=None)
        Traceback (most recent call last):
        ...
        ValueError: NthValue requires a non-null source expression
        """

        msg = "NthValue requires a non-null source expression"
        with self.assertRaisesMessage(ValueError, msg):
            NthValue(expression=None)

    def test_lag_negative_offset(self):
        msg = "Lag requires a positive integer for the offset"
        with self.assertRaisesMessage(ValueError, msg):
            Lag(expression="salary", offset=-1)

    def test_lead_negative_offset(self):
        msg = "Lead requires a positive integer for the offset"
        with self.assertRaisesMessage(ValueError, msg):
            Lead(expression="salary", offset=-1)

    def test_null_source_lead(self):
        msg = "Lead requires a non-null source expression"
        with self.assertRaisesMessage(ValueError, msg):
            Lead(expression=None)

    def test_null_source_lag(self):
        msg = "Lag requires a non-null source expression"
        with self.assertRaisesMessage(ValueError, msg):
            Lag(expression=None)

    def test_negative_num_buckets_ntile(self):
        msg = "num_buckets must be greater than 0"
        with self.assertRaisesMessage(ValueError, msg):
            Ntile(num_buckets=-1)
):
            Ntile(num_buckets=-1)
aisesMessage(ValueError, msg):
            Ntile(num_buckets=-1)
