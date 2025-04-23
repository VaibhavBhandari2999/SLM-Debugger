from django.db.models.functions import Lag, Lead, NthValue, Ntile
from django.test import SimpleTestCase


class ValidationTests(SimpleTestCase):
    def test_nth_negative_nth_value(self):
        """
        Tests the behavior of the NthValue function when a negative integer is provided for the 'nth' parameter.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If 'nth' is a negative integer, with the message "NthValue requires a positive integer as for nth".
        
        Key Points:
        - The function checks if the 'nth' parameter is a negative integer.
        - If 'nth' is negative, a ValueError is raised with a specific message.
        - The function does
        """

        msg = "NthValue requires a positive integer as for nth"
        with self.assertRaisesMessage(ValueError, msg):
            NthValue(expression="salary", nth=-1)

    def test_nth_null_expression(self):
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
        """
        Test for null source expression in Lag function.
        
        This test checks that the Lag function raises a ValueError with an appropriate message when a null source expression is provided.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the source expression is null, with the message "Lag requires a non-null source expression".
        
        Example usage:
        >>> test_null_source_lag()
        ValueError: Lag requires a non-null source expression
        """

        msg = "Lag requires a non-null source expression"
        with self.assertRaisesMessage(ValueError, msg):
            Lag(expression=None)

    def test_negative_num_buckets_ntile(self):
        msg = "num_buckets must be greater than 0"
        with self.assertRaisesMessage(ValueError, msg):
            Ntile(num_buckets=-1)
f.assertRaisesMessage(ValueError, msg):
            Ntile(num_buckets=-1)
1)
