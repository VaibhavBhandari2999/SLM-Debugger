import datetime
import json

from psycopg2.extras import DateRange, DateTimeTZRange, NumericRange, Range

from django.contrib.postgres import forms, lookups
from django.db import models

from .utils import AttributeSetter

__all__ = [
    'RangeField', 'IntegerRangeField', 'BigIntegerRangeField',
    'DecimalRangeField', 'DateTimeRangeField', 'DateRangeField',
    'FloatRangeField',
    'RangeBoundary', 'RangeOperators',
]


class RangeBoundary(models.Expression):
    """A class that represents range boundaries."""
    def __init__(self, inclusive_lower=True, inclusive_upper=False):
        self.lower = '[' if inclusive_lower else '('
        self.upper = ']' if inclusive_upper else ')'

    def as_sql(self, compiler, connection):
        return "'%s%s'" % (self.lower, self.upper), []


class RangeOperators:
    # https://www.postgresql.org/docs/current/functions-range.html#RANGE-OPERATORS-TABLE
    EQUAL = '='
    NOT_EQUAL = '<>'
    CONTAINS = '@>'
    CONTAINED_BY = '<@'
    OVERLAPS = '&&'
    FULLY_LT = '<<'
    FULLY_GT = '>>'
    NOT_LT = '&>'
    NOT_GT = '&<'
    ADJACENT_TO = '-|-'


class RangeField(models.Field):
    empty_strings_allowed = False

    def __init__(self, *args, **kwargs):
        """
        Initialize the object with the given arguments.
        
        This method initializes the object with the provided positional and keyword arguments. It first checks if the object has a 'base_field' attribute. If it does, it initializes the 'base_field' attribute by calling the base_field() method. Then, it calls the superclass's __init__ method with the provided arguments.
        
        Parameters:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
        Returns:
        None: This method does not return
        """

        # Initializing base_field here ensures that its model matches the model for self.
        if hasattr(self, 'base_field'):
            self.base_field = self.base_field()
        super().__init__(*args, **kwargs)

    @property
    def model(self):
        try:
            return self.__dict__['model']
        except KeyError:
            raise AttributeError("'%s' object has no attribute 'model'" % self.__class__.__name__)

    @model.setter
    def model(self, model):
        self.__dict__['model'] = model
        self.base_field.model = model

    def get_prep_value(self, value):
        if value is None:
            return None
        elif isinstance(value, Range):
            return value
        elif isinstance(value, (list, tuple)):
            return self.range_type(value[0], value[1])
        return value

    def to_python(self, value):
        """
        Converts a given value to a Python object.
        
        This method is used to deserialize a string representation of a range or to convert a list or tuple into a range object. The function handles the following cases:
        
        - If the input value is a string, it is assumed to be a JSON string representing a dictionary with keys 'lower' and 'upper'. The values corresponding to these keys are converted to the appropriate type using the `to_python` method of the `base_field` object. The resulting dictionary
        """

        if isinstance(value, str):
            # Assume we're deserializing
            vals = json.loads(value)
            for end in ('lower', 'upper'):
                if end in vals:
                    vals[end] = self.base_field.to_python(vals[end])
            value = self.range_type(**vals)
        elif isinstance(value, (list, tuple)):
            value = self.range_type(value[0], value[1])
        return value

    def set_attributes_from_name(self, name):
        super().set_attributes_from_name(name)
        self.base_field.set_attributes_from_name(name)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        if value is None:
            return None
        if value.isempty:
            return json.dumps({"empty": True})
        base_field = self.base_field
        result = {"bounds": value._bounds}
        for end in ('lower', 'upper'):
            val = getattr(value, end)
            if val is None:
                result[end] = None
            else:
                obj = AttributeSetter(base_field.attname, val)
                result[end] = base_field.value_to_string(obj)
        return json.dumps(result)

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', self.form_field)
        return super().formfield(**kwargs)


class IntegerRangeField(RangeField):
    base_field = models.IntegerField
    range_type = NumericRange
    form_field = forms.IntegerRangeField

    def db_type(self, connection):
        return 'int4range'


class BigIntegerRangeField(RangeField):
    base_field = models.BigIntegerField
    range_type = NumericRange
    form_field = forms.IntegerRangeField

    def db_type(self, connection):
        return 'int8range'


class DecimalRangeField(RangeField):
    base_field = models.DecimalField
    range_type = NumericRange
    form_field = forms.DecimalRangeField

    def db_type(self, connection):
        return 'numrange'


class FloatRangeField(RangeField):
    system_check_deprecated_details = {
        'msg': (
            'FloatRangeField is deprecated and will be removed in Django 3.1.'
        ),
        'hint': 'Use DecimalRangeField instead.',
        'id': 'fields.W902',
    }
    base_field = models.FloatField
    range_type = NumericRange
    form_field = forms.FloatRangeField

    def db_type(self, connection):
        return 'numrange'


class DateTimeRangeField(RangeField):
    base_field = models.DateTimeField
    range_type = DateTimeTZRange
    form_field = forms.DateTimeRangeField

    def db_type(self, connection):
        return 'tstzrange'


class DateRangeField(RangeField):
    base_field = models.DateField
    range_type = DateRange
    form_field = forms.DateRangeField

    def db_type(self, connection):
        return 'daterange'


RangeField.register_lookup(lookups.DataContains)
RangeField.register_lookup(lookups.ContainedBy)
RangeField.register_lookup(lookups.Overlap)


class DateTimeRangeContains(lookups.PostgresSimpleLookup):
    """
    Lookup for Date/DateTimeRange containment to cast the rhs to the correct
    type.
    """
    lookup_name = 'contains'
    operator = RangeOperators.CONTAINS

    def process_rhs(self, compiler, connection):
        """
        Transforms the right-hand side (rhs) value for database lookup.
        
        This method is responsible for converting the rhs value to a format suitable for database queries. It checks if the rhs value is a datetime.date object and then determines the appropriate output field type (DateTimeField or DateField) based on whether the rhs is a datetime.datetime or datetime.date object. The rhs value is then wrapped in a Value object with the determined output field and resolved using the compiler's query.
        
        Parameters:
        compiler (object
        """

        # Transform rhs value for db lookup.
        if isinstance(self.rhs, datetime.date):
            output_field = models.DateTimeField() if isinstance(self.rhs, datetime.datetime) else models.DateField()
            value = models.Value(self.rhs, output_field=output_field)
            self.rhs = value.resolve_expression(compiler.query)
        return super().process_rhs(compiler, connection)

    def as_sql(self, compiler, connection):
        sql, params = super().as_sql(compiler, connection)
        # Cast the rhs if needed.
        cast_sql = ''
        if (
            isinstance(self.rhs, models.Expression) and
            self.rhs._output_field_or_none and
            # Skip cast if rhs has a matching range type.
            not isinstance(self.rhs._output_field_or_none, self.lhs.output_field.__class__)
        ):
            cast_internal_type = self.lhs.output_field.base_field.get_internal_type()
            cast_sql = '::{}'.format(connection.data_types.get(cast_internal_type))
        return '%s%s' % (sql, cast_sql), params


DateRangeField.register_lookup(DateTimeRangeContains)
DateTimeRangeField.register_lookup(DateTimeRangeContains)


class RangeContainedBy(lookups.PostgresSimpleLookup):
    lookup_name = 'contained_by'
    type_mapping = {
        'integer': 'int4range',
        'bigint': 'int8range',
        'double precision': 'numrange',
        'date': 'daterange',
        'timestamp with time zone': 'tstzrange',
    }
    operator = RangeOperators.CONTAINED_BY

    def process_rhs(self, compiler, connection):
        rhs, rhs_params = super().process_rhs(compiler, connection)
        cast_type = self.type_mapping[self.lhs.output_field.db_type(connection)]
        return '%s::%s' % (rhs, cast_type), rhs_params

    def process_lhs(self, compiler, connection):
        lhs, lhs_params = super().process_lhs(compiler, connection)
        if isinstance(self.lhs.output_field, models.FloatField):
            lhs = '%s::numeric' % lhs
        return lhs, lhs_params

    def get_prep_lookup(self):
        return RangeField().get_prep_value(self.rhs)


models.DateField.register_lookup(RangeContainedBy)
models.DateTimeField.register_lookup(RangeContainedBy)
models.IntegerField.register_lookup(RangeContainedBy)
models.BigIntegerField.register_lookup(RangeContainedBy)
models.FloatField.register_lookup(RangeContainedBy)


@RangeField.register_lookup
class FullyLessThan(lookups.PostgresSimpleLookup):
    lookup_name = 'fully_lt'
    operator = RangeOperators.FULLY_LT


@RangeField.register_lookup
class FullGreaterThan(lookups.PostgresSimpleLookup):
    lookup_name = 'fully_gt'
    operator = RangeOperators.FULLY_GT


@RangeField.register_lookup
class NotLessThan(lookups.PostgresSimpleLookup):
    lookup_name = 'not_lt'
    operator = RangeOperators.NOT_LT


@RangeField.register_lookup
class NotGreaterThan(lookups.PostgresSimpleLookup):
    lookup_name = 'not_gt'
    operator = RangeOperators.NOT_GT


@RangeField.register_lookup
class AdjacentToLookup(lookups.PostgresSimpleLookup):
    lookup_name = 'adjacent_to'
    operator = RangeOperators.ADJACENT_TO


@RangeField.register_lookup
class RangeStartsWith(models.Transform):
    lookup_name = 'startswith'
    function = 'lower'

    @property
    def output_field(self):
        return self.lhs.output_field.base_field


@RangeField.register_lookup
class RangeEndsWith(models.Transform):
    lookup_name = 'endswith'
    function = 'upper'

    @property
    def output_field(self):
        return self.lhs.output_field.base_field


@RangeField.register_lookup
class IsEmpty(models.Transform):
    lookup_name = 'isempty'
    function = 'isempty'
    output_field = models.BooleanField()
