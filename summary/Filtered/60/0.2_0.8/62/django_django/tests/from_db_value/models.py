import decimal

from django.db import models


class Cash(decimal.Decimal):
    currency = 'USD'


class CashField(models.DecimalField):
    def __init__(self, **kwargs):
        """
        Initialize a DecimalField with specified parameters.
        
        This method initializes a DecimalField with default settings for max_digits and decimal_places.
        
        Parameters:
        **kwargs (dict): Arbitrary keyword arguments to be passed to the superclass.
        
        Keyword Arguments:
        max_digits (int): The maximum number of digits the decimal can have (default is 20).
        decimal_places (int): The number of decimal places the decimal can have (default is 2).
        
        Returns:
        None: This method does not return any value
        """

        kwargs['max_digits'] = 20
        kwargs['decimal_places'] = 2
        super().__init__(**kwargs)

    def from_db_value(self, value, expression, connection):
        """
        from_db_value(self, value, expression, connection) -> Cash
        
        Converts a database value to a Cash object. The function takes three parameters:
        - value: The raw value retrieved from the database.
        - expression: The expression used to retrieve the value from the database.
        - connection: The database connection object, which is used to determine the vendor-specific behavior.
        
        Returns:
        - A Cash object initialized with the provided value and the vendor information from the connection object.
        """

        cash = Cash(value)
        cash.vendor = connection.vendor
        return cash


class CashModel(models.Model):
    cash = CashField()
