from django.contrib.postgres.fields import ArrayField, JSONField
from django.db.models import Aggregate, Value

from .mixins import OrderableAggMixin

__all__ = [
    'ArrayAgg', 'BitAnd', 'BitOr', 'BoolAnd', 'BoolOr', 'JSONBAgg', 'StringAgg',
]


class ArrayAgg(OrderableAggMixin, Aggregate):
    function = 'ARRAY_AGG'
    template = '%(function)s(%(distinct)s%(expressions)s %(ordering)s)'
    allow_distinct = True

    @property
    def output_field(self):
        return ArrayField(self.source_expressions[0].output_field)

    def convert_value(self, value, expression, connection):
        """
        Converts a given value to a list based on the provided expression and connection.
        
        Parameters:
        value (Any): The input value to be converted.
        expression (str): The expression used for conversion.
        connection (Connection): The database connection object.
        
        Returns:
        list: A list of values derived from the input value.
        
        Note:
        - If the input value is None, an empty list is returned.
        """

        if not value:
            return []
        return value


class BitAnd(Aggregate):
    function = 'BIT_AND'


class BitOr(Aggregate):
    function = 'BIT_OR'


class BoolAnd(Aggregate):
    function = 'BOOL_AND'


class BoolOr(Aggregate):
    function = 'BOOL_OR'


class JSONBAgg(Aggregate):
    function = 'JSONB_AGG'
    output_field = JSONField()

    def convert_value(self, value, expression, connection):
        if not value:
            return []
        return value


class StringAgg(OrderableAggMixin, Aggregate):
    function = 'STRING_AGG'
    template = '%(function)s(%(distinct)s%(expressions)s %(ordering)s)'
    allow_distinct = True

    def __init__(self, expression, delimiter, **extra):
        delimiter_expr = Value(str(delimiter))
        super().__init__(expression, delimiter_expr, **extra)

    def convert_value(self, value, expression, connection):
        """
        Converts a given value to a string representation.
        
        This method takes a value and converts it to a string. If the value is None, it returns an empty string.
        
        Parameters:
        value (Any): The value to be converted to a string.
        expression (str): The expression associated with the value.
        connection (Connection): The database connection object.
        
        Returns:
        str: The string representation of the value or an empty string if the value is None.
        """

        if not value:
            return ''
        return value
