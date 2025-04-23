import decimal

from django.db import models


class Cash(decimal.Decimal):
    currency = 'USD'


class CashField(models.DecimalField):
    def __init__(self, **kwargs):
        """
        Initialize a DecimalField instance.
        
        This method sets up a DecimalField with specified attributes.
        
        Parameters:
        **kwargs (dict): Arbitrary keyword arguments to configure the DecimalField.
        The following keys are recognized and set:
        - max_digits: The maximum number of digits the decimal can have (default is 20).
        - decimal_places: The number of decimal places the decimal can have (default is 2).
        
        Note:
        If 'max_digits' and 'decimal_places' are not
        """

        kwargs['max_digits'] = 20
        kwargs['decimal_places'] = 2
        super().__init__(**kwargs)

    def from_db_value(self, value, expression, connection):
        cash = Cash(value)
        cash.vendor = connection.vendor
        return cash


class CashModel(models.Model):
    cash = CashField()
