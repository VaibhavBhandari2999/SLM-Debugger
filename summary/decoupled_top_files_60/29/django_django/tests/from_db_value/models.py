import decimal

from django.db import models


class Cash(decimal.Decimal):
    currency = 'USD'

    def __str__(self):
        s = super().__str__(self)
        return '%s %s' % (s, self.currency)


class CashField(models.DecimalField):
    def __init__(self, **kwargs):
        """
        Initialize a DecimalField instance with specified parameters.
        
        Args:
        **kwargs (dict): Arbitrary keyword arguments to be passed to the superclass.
        
        This method sets the 'max_digits' to 20 and 'decimal_places' to 2 before calling the superclass's __init__ method with the updated kwargs.
        """

        kwargs['max_digits'] = 20
        kwargs['decimal_places'] = 2
        super().__init__(**kwargs)

    def from_db_value(self, value, expression, connection):
        """
        from_db_value(self, value, expression, connection) -> Cash
        
        Converts a value from the database into a Cash object.
        
        Parameters:
        - value: The value retrieved from the database.
        - expression: The database expression used to retrieve the value.
        - connection: The database connection object.
        
        Returns:
        - A Cash object initialized with the provided value and the connection's vendor.
        """

        cash = Cash(value)
        cash.vendor = connection.vendor
        return cash


class CashModel(models.Model):
    cash = CashField()

    def __str__(self):
        return str(self.cash)
