import decimal

from django.db import models


class Cash(decimal.Decimal):
    currency = 'USD'


class CashField(models.DecimalField):
    def __init__(self, **kwargs):
        """
        Initialize a DecimalField instance.
        
        This method sets up the DecimalField with specified attributes.
        
        Parameters:
        **kwargs: Arbitrary keyword arguments to configure the field.
        The 'max_digits' and 'decimal_places' are set to 20 and 2 respectively.
        
        Returns:
        None: This method does not return any value. It initializes the DecimalField instance.
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
