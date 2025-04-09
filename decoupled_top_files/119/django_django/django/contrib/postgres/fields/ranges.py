import datetime
import json

from django.contrib.postgres import forms, lookups
from django.db import models
from django.db.backends.postgresql.psycopg_any import (
    DateRange,
    DateTimeTZRange,
    NumericRange,
    Range,
)
from django.db.models.functions import Cast
from django.db.models.lookups import PostgresOperatorLookup

from .utils import AttributeSetter

__all__ = [
    "RangeField",
    "IntegerRangeField",
    "BigIntegerRangeField",
    "DecimalRangeField",
    "DateTimeRangeField",
    "DateRangeField",
    "RangeBoundary",
    "RangeOperators",
]


class RangeBoundary(models.Expression):
    """A class that represents range boundaries."""

    def __init__(self, inclusive_lower=True, inclusive_upper=False):
        self.lower = "[" if inclusive_lower else "("
        self.upper = "]" if inclusive_upper else ")"

    def as_sql(self, compiler, connection):
        return "'%s%s'" % (self.lower, self.upper), []


class RangeOperators:
    # https://www.postgresql.org/docs/current/functions-range.html#RANGE-OPERATORS-TABLE
    EQUAL = "="
    NOT_EQUAL = "<>"
    CONTAINS = "@>"
    CONTAINED_BY = "<@"
    OVERLAPS = "&&"
    FULLY_LT = "<<"
    FULLY_GT = ">>"
    NOT_LT = "&>"
    NOT_GT = "&<"
    ADJACENT_TO = "-|-"


class RangeField(models.Field):
    empty_strings_allowed = False

    def __init__(self, *args, **kwargs):
        """
        Initialize the object with the given arguments.
        
        Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
        Raises:
        TypeError: If 'default_bounds' is provided in kwargs.
        
        Notes:
        - The `base_field` attribute is initialized using the `base_field()` method.
        - The `super().__init__()` method is called to initialize the parent class.
        """

        if "default_bounds" in kwargs:
            raise TypeError(
                f"Cannot use 'default_bounds' with {self.__class__.__name__}."
            )
        # Initializing base_field here ensures that its model matches the model
        # for self.
        if hasattr(self, "base_field"):
            self.base_field = self.base_field()
        super().__init__(*args, **kwargs)

    @property
    def model(self):
        """
        Retrieve the model attribute.
        
        This method attempts to access the 'model' attribute from the instance's
        dictionary. If the attribute does not exist, it raises an `AttributeError`
        with a descriptive message indicating the class name and the missing
        attribute.
        
        Returns:
        The value of the 'model' attribute.
        
        Raises:
        AttributeError: If the 'model' attribute is not found in the instance's
        dictionary.
        
        Notes:
        - The method uses the `
        """

        try:
            return self.__dict__["model"]
        except KeyError:
            raise AttributeError(
                "'%s' object has no attribute 'model'" % self.__class__.__name__
            )

    @model.setter
    def model(self, model):
        self.__dict__["model"] = model
        self.base_field.model = model

    @classmethod
    def _choices_is_value(cls, value):
        return isinstance(value, (list, tuple)) or super()._choices_is_value(value)

    def get_placeholder(self, value, compiler, connection):
        return "%s::{}".format(self.db_type(connection))

    def get_prep_value(self, value):
        """
        Get the prepared value for the range field.
        
        This method processes the input value and returns a prepared value
        that can be stored in the database. It handles different types of inputs,
        including `None`, `Range` objects, lists, and tuples.
        
        Args:
        value: The input value to be processed.
        
        Returns:
        A prepared value that can be stored in the database, which could be
        a `Range` object or a newly created `Range` object from
        """

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
        
        Args:
        value: The input value to be converted.
        
        Returns:
        A Python object representing the input value.
        
        Summary:
        This function handles the conversion of a string or list/tuple input to a Python object. It uses the `json.loads` function to parse the string input and the `to_python` method of the `base_field` object to process the 'lower' and 'upper' values. For list/tuple
        """

        if isinstance(value, str):
            # Assume we're deserializing
            vals = json.loads(value)
            for end in ("lower", "upper"):
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
        """
        Converts an object's value to a JSON string representation.
        
        This function takes an object, extracts its value using `value_from_object`,
        and processes it based on whether it is `None` or empty. If the value is not
        `None` and is not empty, it constructs a dictionary containing bounds and
        lower/upper values, converting these values to strings using the `base_field`
        attribute's `value_to_string` method. The final result is returned as a
        """

        value = self.value_from_object(obj)
        if value is None:
            return None
        if value.isempty:
            return json.dumps({"empty": True})
        base_field = self.base_field
        result = {"bounds": value._bounds}
        for end in ("lower", "upper"):
            val = getattr(value, end)
            if val is None:
                result[end] = None
            else:
                obj = AttributeSetter(base_field.attname, val)
                result[end] = base_field.value_to_string(obj)
        return json.dumps(result)

    def formfield(self, **kwargs):
        kwargs.setdefault("form_class", self.form_field)
        return super().formfield(**kwargs)


CANONICAL_RANGE_BOUNDS = "[)"


class ContinuousRangeField(RangeField):
    """
    Continuous range field. It allows specifying default bounds for list and
    tuple inputs.
    """

    def __init__(self, *args, default_bounds=CANONICAL_RANGE_BOUNDS, **kwargs):
        """
        Initialize the object with the specified bounds.
        
        Args:
        *args: Variable length argument list.
        default_bounds (str): The default bounds for the object. Must be one of '[)', '(]', '()', or '[]'.
        **kwargs: Arbitrary keyword arguments.
        
        Raises:
        ValueError: If `default_bounds` is not one of '[)', '(]', '()', or '[]'.
        
        Attributes:
        default_bounds (str): The default bounds for the object.
        """

        if default_bounds not in ("[)", "(]", "()", "[]"):
            raise ValueError("default_bounds must be one of '[)', '(]', '()', or '[]'.")
        self.default_bounds = default_bounds
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        """
        Get the prepared value for the given input.
        
        This method processes the input value and returns a prepared value
        suitable for database storage. It handles lists or tuples by creating
        an instance of `range_type` with the first and second elements of the
        list or tuple. For other types of inputs, it delegates to the parent
        class's `get_prep_value` method.
        
        Args:
        value: The input value to be processed.
        
        Returns:
        The prepared value
        """

        if isinstance(value, (list, tuple)):
            return self.range_type(value[0], value[1], self.default_bounds)
        return super().get_prep_value(value)

    def formfield(self, **kwargs):
        kwargs.setdefault("default_bounds", self.default_bounds)
        return super().formfield(**kwargs)

    def deconstruct(self):
        """
        Deconstructs the object into its constituent parts.
        
        This method is used to break down the object into its fundamental components, such as the name, path, arguments, and keyword arguments. It also handles the `default_bounds` attribute, ensuring that it is included in the deconstruction process if it has been set and is not the default value.
        
        Args:
        None (This method is called automatically by Django's serialization framework.)
        
        Returns:
        tuple: A tuple containing the name, path
        """

        name, path, args, kwargs = super().deconstruct()
        if self.default_bounds and self.default_bounds != CANONICAL_RANGE_BOUNDS:
            kwargs["default_bounds"] = self.default_bounds
        return name, path, args, kwargs


class IntegerRangeField(RangeField):
    base_field = models.IntegerField
    range_type = NumericRange
    form_field = forms.IntegerRangeField

    def db_type(self, connection):
        return "int4range"


class BigIntegerRangeField(RangeField):
    base_field = models.BigIntegerField
    range_type = NumericRange
    form_field = forms.IntegerRangeField

    def db_type(self, connection):
        return "int8range"


class DecimalRangeField(ContinuousRangeField):
    base_field = models.DecimalField
    range_type = NumericRange
    form_field = forms.DecimalRangeField

    def db_type(self, connection):
        return "numrange"


class DateTimeRangeField(ContinuousRangeField):
    base_field = models.DateTimeField
    range_type = DateTimeTZRange
    form_field = forms.DateTimeRangeField

    def db_type(self, connection):
        return "tstzrange"


class DateRangeField(RangeField):
    base_field = models.DateField
    range_type = DateRange
    form_field = forms.DateRangeField

    def db_type(self, connection):
        return "daterange"


class RangeContains(lookups.DataContains):
    def get_prep_lookup(self):
        """
        Generates a prepared lookup value for database queries.
        
        This method processes the right-hand side (rhs) of a lookup expression
        and prepares it for use in database queries. If `rhs` is not a list,
        tuple, or instance of `Range`, it casts `rhs` to the base field type of
        the left-hand side (lhs) field's base field. Otherwise, it delegates
        the preparation to the superclass method.
        
        Args:
        self: The current
        """

        if not isinstance(self.rhs, (list, tuple, Range)):
            return Cast(self.rhs, self.lhs.field.base_field)
        return super().get_prep_lookup()


RangeField.register_lookup(RangeContains)
RangeField.register_lookup(lookups.ContainedBy)
RangeField.register_lookup(lookups.Overlap)


class DateTimeRangeContains(PostgresOperatorLookup):
    """
    Lookup for Date/DateTimeRange containment to cast the rhs to the correct
    type.
    """

    lookup_name = "contains"
    postgres_operator = RangeOperators.CONTAINS

    def process_rhs(self, compiler, connection):
        """
        Processes the right-hand side (rhs) value for database lookup.
        
        Args:
        compiler: The SQL compiler instance.
        connection: The database connection object.
        
        Returns:
        The processed rhs value after transformation.
        
        Summary:
        This method transforms the rhs value for database lookup. If the rhs is an instance of `datetime.date`, it resolves the expression using the provided compiler and query. Otherwise, it delegates the processing to the superclass method.
        """

        # Transform rhs value for db lookup.
        if isinstance(self.rhs, datetime.date):
            value = models.Value(self.rhs)
            self.rhs = value.resolve_expression(compiler.query)
        return super().process_rhs(compiler, connection)

    def as_postgresql(self, compiler, connection):
        """
        Generates a PostgreSQL-specific SQL query for the given expression.
        
        Args:
        compiler: The SQL compiler instance.
        connection: The database connection object.
        
        Returns:
        A tuple containing the generated SQL query and parameters.
        
        This method is responsible for generating a PostgreSQL-specific SQL query for the given expression. It first calls the superclass's `as_postgresql` method to get the initial SQL query and parameters. Then, it checks if the right-hand side (rhs) of the expression is an
        """

        sql, params = super().as_postgresql(compiler, connection)
        # Cast the rhs if needed.
        cast_sql = ""
        if (
            isinstance(self.rhs, models.Expression)
            and self.rhs._output_field_or_none
            and
            # Skip cast if rhs has a matching range type.
            not isinstance(
                self.rhs._output_field_or_none, self.lhs.output_field.__class__
            )
        ):
            cast_internal_type = self.lhs.output_field.base_field.get_internal_type()
            cast_sql = "::{}".format(connection.data_types.get(cast_internal_type))
        return "%s%s" % (sql, cast_sql), params


DateRangeField.register_lookup(DateTimeRangeContains)
DateTimeRangeField.register_lookup(DateTimeRangeContains)


class RangeContainedBy(PostgresOperatorLookup):
    lookup_name = "contained_by"
    type_mapping = {
        "smallint": "int4range",
        "integer": "int4range",
        "bigint": "int8range",
        "double precision": "numrange",
        "numeric": "numrange",
        "date": "daterange",
        "timestamp with time zone": "tstzrange",
    }
    postgres_operator = RangeOperators.CONTAINED_BY

    def process_rhs(self, compiler, connection):
        """
        Processes the right-hand side of a query for a specific field type.
        
        Args:
        compiler: The SQL compiler instance.
        connection: The database connection object.
        
        Returns:
        A tuple containing the processed right-hand side expression and its parameters.
        """

        rhs, rhs_params = super().process_rhs(compiler, connection)
        # Ignore precision for DecimalFields.
        db_type = self.lhs.output_field.cast_db_type(connection).split("(")[0]
        cast_type = self.type_mapping[db_type]
        return "%s::%s" % (rhs, cast_type), rhs_params

    def process_lhs(self, compiler, connection):
        """
        Processes the left-hand side of a query expression.
        
        Args:
        compiler: The SQL compiler instance.
        connection: The database connection object.
        
        Returns:
        A tuple containing the processed left-hand side and its parameters.
        
        Notes:
        - This method is overridden from a superclass.
        - It processes the left-hand side based on the output field type.
        - If the field is a `FloatField`, it casts the left-hand side to `numeric`.
        - If the field is
        """

        lhs, lhs_params = super().process_lhs(compiler, connection)
        if isinstance(self.lhs.output_field, models.FloatField):
            lhs = "%s::numeric" % lhs
        elif isinstance(self.lhs.output_field, models.SmallIntegerField):
            lhs = "%s::integer" % lhs
        return lhs, lhs_params

    def get_prep_lookup(self):
        return RangeField().get_prep_value(self.rhs)


models.DateField.register_lookup(RangeContainedBy)
models.DateTimeField.register_lookup(RangeContainedBy)
models.IntegerField.register_lookup(RangeContainedBy)
models.FloatField.register_lookup(RangeContainedBy)
models.DecimalField.register_lookup(RangeContainedBy)


@RangeField.register_lookup
class FullyLessThan(PostgresOperatorLookup):
    lookup_name = "fully_lt"
    postgres_operator = RangeOperators.FULLY_LT


@RangeField.register_lookup
class FullGreaterThan(PostgresOperatorLookup):
    lookup_name = "fully_gt"
    postgres_operator = RangeOperators.FULLY_GT


@RangeField.register_lookup
class NotLessThan(PostgresOperatorLookup):
    lookup_name = "not_lt"
    postgres_operator = RangeOperators.NOT_LT


@RangeField.register_lookup
class NotGreaterThan(PostgresOperatorLookup):
    lookup_name = "not_gt"
    postgres_operator = RangeOperators.NOT_GT


@RangeField.register_lookup
class AdjacentToLookup(PostgresOperatorLookup):
    lookup_name = "adjacent_to"
    postgres_operator = RangeOperators.ADJACENT_TO


@RangeField.register_lookup
class RangeStartsWith(models.Transform):
    lookup_name = "startswith"
    function = "lower"

    @property
    def output_field(self):
        return self.lhs.output_field.base_field


@RangeField.register_lookup
class RangeEndsWith(models.Transform):
    lookup_name = "endswith"
    function = "upper"

    @property
    def output_field(self):
        return self.lhs.output_field.base_field


@RangeField.register_lookup
class IsEmpty(models.Transform):
    lookup_name = "isempty"
    function = "isempty"
    output_field = models.BooleanField()


@RangeField.register_lookup
class LowerInclusive(models.Transform):
    lookup_name = "lower_inc"
    function = "LOWER_INC"
    output_field = models.BooleanField()


@RangeField.register_lookup
class LowerInfinite(models.Transform):
    lookup_name = "lower_inf"
    function = "LOWER_INF"
    output_field = models.BooleanField()


@RangeField.register_lookup
class UpperInclusive(models.Transform):
    lookup_name = "upper_inc"
    function = "UPPER_INC"
    output_field = models.BooleanField()


@RangeField.register_lookup
class UpperInfinite(models.Transform):
    lookup_name = "upper_inf"
    function = "UPPER_INF"
    output_field = models.BooleanField()
