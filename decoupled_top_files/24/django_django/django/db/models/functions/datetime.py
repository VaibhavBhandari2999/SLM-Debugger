from datetime import datetime

from django.conf import settings
from django.db.models.expressions import Func
from django.db.models.fields import (
    DateField, DateTimeField, DurationField, Field, IntegerField, TimeField,
)
from django.db.models.lookups import (
    Transform, YearExact, YearGt, YearGte, YearLt, YearLte,
)
from django.utils import timezone


class TimezoneMixin:
    tzinfo = None

    def get_tzname(self):
        """
        Gets the timezone name for the given datetime.
        
        Args:
        self (datetime): The input datetime object.
        
        Returns:
        str: The timezone name of the input datetime.
        
        Notes:
        - If USE_TZ is enabled, the timezone name is determined based on the input datetime's timezone information.
        - If the input datetime has no timezone information, the current timezone is used.
        - The function returns `None` if USE_TZ is disabled.
        """

        # Timezone conversions must happen to the input datetime *before*
        # applying a function. 2015-12-31 23:00:00 -02:00 is stored in the
        # database as 2016-01-01 01:00:00 +00:00. Any results should be
        # based on the input datetime not the stored datetime.
        tzname = None
        if settings.USE_TZ:
            if self.tzinfo is None:
                tzname = timezone.get_current_timezone_name()
            else:
                tzname = timezone._get_timezone_name(self.tzinfo)
        return tzname


class Extract(TimezoneMixin, Transform):
    lookup_name = None
    output_field = IntegerField()

    def __init__(self, expression, lookup_name=None, tzinfo=None, **extra):
        """
        Initialize a new instance of the class.
        
        Args:
        expression (str): The expression to be evaluated.
        lookup_name (str, optional): The name of the lookup. Defaults to None.
        tzinfo (datetime.tzinfo, optional): Time zone information. Defaults to None.
        extra (dict): Additional keyword arguments.
        
        Raises:
        ValueError: If `lookup_name` is not provided.
        
        Attributes:
        lookup_name (str): The name of the lookup.
        tz
        """

        if self.lookup_name is None:
            self.lookup_name = lookup_name
        if self.lookup_name is None:
            raise ValueError('lookup_name must be provided')
        self.tzinfo = tzinfo
        super().__init__(expression, **extra)

    def as_sql(self, compiler, connection):
        """
        Generates SQL for extracting a specific part of a datetime or date field.
        
        Args:
        compiler (Compiler): The compiler object responsible for compiling the query.
        connection (Connection): The database connection object.
        
        Returns:
        tuple: A tuple containing the generated SQL and parameters.
        
        Raises:
        ValueError: If the database does not support native duration field extraction.
        
        Important Functions:
        - `compiler.compile(self.lhs)`: Compiles the left-hand side of the expression.
        -
        """

        sql, params = compiler.compile(self.lhs)
        lhs_output_field = self.lhs.output_field
        if isinstance(lhs_output_field, DateTimeField):
            tzname = self.get_tzname()
            sql = connection.ops.datetime_extract_sql(self.lookup_name, sql, tzname)
        elif isinstance(lhs_output_field, DateField):
            sql = connection.ops.date_extract_sql(self.lookup_name, sql)
        elif isinstance(lhs_output_field, TimeField):
            sql = connection.ops.time_extract_sql(self.lookup_name, sql)
        elif isinstance(lhs_output_field, DurationField):
            if not connection.features.has_native_duration_field:
                raise ValueError('Extract requires native DurationField database support.')
            sql = connection.ops.time_extract_sql(self.lookup_name, sql)
        else:
            # resolve_expression has already validated the output_field so this
            # assert should never be hit.
            assert False, "Tried to Extract from an invalid type."
        return sql, params

    def resolve_expression(self, query=None, allow_joins=True, reuse=None, summarize=False, for_save=False):
        """
        Resolves an expression for extracting specific components from date, datetime, time, or duration fields.
        
        Args:
        query: The query object to which the expression is being added.
        allow_joins: A boolean indicating whether joins are allowed in the query.
        reuse: An optional instance of the same class to reuse.
        summarize: A boolean indicating whether the expression is being used for summarization.
        for_save: A boolean indicating whether the expression is being used for saving.
        
        Returns:
        """

        copy = super().resolve_expression(query, allow_joins, reuse, summarize, for_save)
        field = copy.lhs.output_field
        if not isinstance(field, (DateField, DateTimeField, TimeField, DurationField)):
            raise ValueError(
                'Extract input expression must be DateField, DateTimeField, '
                'TimeField, or DurationField.'
            )
        # Passing dates to functions expecting datetimes is most likely a mistake.
        if type(field) == DateField and copy.lookup_name in ('hour', 'minute', 'second'):
            raise ValueError(
                "Cannot extract time component '%s' from DateField '%s'. " % (copy.lookup_name, field.name)
            )
        if (
            isinstance(field, DurationField) and
            copy.lookup_name in ('year', 'iso_year', 'month', 'week', 'week_day', 'quarter')
        ):
            raise ValueError(
                "Cannot extract component '%s' from DurationField '%s'."
                % (copy.lookup_name, field.name)
            )
        return copy


class ExtractYear(Extract):
    lookup_name = 'year'


class ExtractIsoYear(Extract):
    """Return the ISO-8601 week-numbering year."""
    lookup_name = 'iso_year'


class ExtractMonth(Extract):
    lookup_name = 'month'


class ExtractDay(Extract):
    lookup_name = 'day'


class ExtractWeek(Extract):
    """
    Return 1-52 or 53, based on ISO-8601, i.e., Monday is the first of the
    week.
    """
    lookup_name = 'week'


class ExtractWeekDay(Extract):
    """
    Return Sunday=1 through Saturday=7.

    To replicate this in Python: (mydatetime.isoweekday() % 7) + 1
    """
    lookup_name = 'week_day'


class ExtractQuarter(Extract):
    lookup_name = 'quarter'


class ExtractHour(Extract):
    lookup_name = 'hour'


class ExtractMinute(Extract):
    lookup_name = 'minute'


class ExtractSecond(Extract):
    lookup_name = 'second'


DateField.register_lookup(ExtractYear)
DateField.register_lookup(ExtractMonth)
DateField.register_lookup(ExtractDay)
DateField.register_lookup(ExtractWeekDay)
DateField.register_lookup(ExtractWeek)
DateField.register_lookup(ExtractIsoYear)
DateField.register_lookup(ExtractQuarter)

TimeField.register_lookup(ExtractHour)
TimeField.register_lookup(ExtractMinute)
TimeField.register_lookup(ExtractSecond)

DateTimeField.register_lookup(ExtractHour)
DateTimeField.register_lookup(ExtractMinute)
DateTimeField.register_lookup(ExtractSecond)

ExtractYear.register_lookup(YearExact)
ExtractYear.register_lookup(YearGt)
ExtractYear.register_lookup(YearGte)
ExtractYear.register_lookup(YearLt)
ExtractYear.register_lookup(YearLte)

ExtractIsoYear.register_lookup(YearExact)
ExtractIsoYear.register_lookup(YearGt)
ExtractIsoYear.register_lookup(YearGte)
ExtractIsoYear.register_lookup(YearLt)
ExtractIsoYear.register_lookup(YearLte)


class Now(Func):
    template = 'CURRENT_TIMESTAMP'
    output_field = DateTimeField()

    def as_postgresql(self, compiler, connection, **extra_context):
        """
        Returns the current statement timestamp using the 'STATEMENT_TIMESTAMP()' function, which is cross-compatible with other databases. This function is typically used in SQL queries to get the timestamp when the statement was executed.
        
        Args:
        compiler (Compiler): The SQL compiler object used to generate the SQL query.
        connection (Connection): The database connection object.
        extra_context (dict): Additional context parameters.
        
        Returns:
        str: The SQL query string representing the current statement timestamp.
        """

        # PostgreSQL's CURRENT_TIMESTAMP means "the time at the start of the
        # transaction". Use STATEMENT_TIMESTAMP to be cross-compatible with
        # other databases.
        return self.as_sql(compiler, connection, template='STATEMENT_TIMESTAMP()', **extra_context)


class TruncBase(TimezoneMixin, Transform):
    kind = None
    tzinfo = None

    def __init__(self, expression, output_field=None, tzinfo=None, is_dst=None, **extra):
        """
        Initializes a timezone-aware datetime expression.
        
        Args:
        expression (str): The datetime expression to be evaluated.
        output_field (Field, optional): The output field for the expression. Defaults to None.
        tzinfo (datetime.tzinfo, optional): The timezone information. Defaults to None.
        is_dst (bool, optional): Indicates whether daylight saving time is in effect. Defaults to None.
        
        Returns:
        A timezone-aware datetime object based on the provided expression and timezone information.
        """

        self.tzinfo = tzinfo
        self.is_dst = is_dst
        super().__init__(expression, output_field=output_field, **extra)

    def as_sql(self, compiler, connection):
        """
        Truncates a datetime, date, or time value to a specified level of precision.
        
        Args:
        compiler (Compiler): The SQL compiler instance used to compile the left-hand side expression.
        connection (Connection): The database connection object.
        
        Returns:
        tuple: A tuple containing the generated SQL query and the parameters required for execution.
        
        Raises:
        ValueError: If the output field is not a DateField, TimeField, or DateTimeField.
        
        Important Functions:
        - `compiler
        """

        inner_sql, inner_params = compiler.compile(self.lhs)
        if isinstance(self.output_field, DateTimeField):
            tzname = self.get_tzname()
            sql = connection.ops.datetime_trunc_sql(self.kind, inner_sql, tzname)
        elif isinstance(self.output_field, DateField):
            sql = connection.ops.date_trunc_sql(self.kind, inner_sql)
        elif isinstance(self.output_field, TimeField):
            sql = connection.ops.time_trunc_sql(self.kind, inner_sql)
        else:
            raise ValueError('Trunc only valid on DateField, TimeField, or DateTimeField.')
        return sql, inner_params

    def resolve_expression(self, query=None, allow_joins=True, reuse=None, summarize=False, for_save=False):
        """
        Resolves an expression to a specific field type.
        
        Args:
        query: The query object.
        allow_joins: Whether joins are allowed.
        reuse: An existing node to reuse.
        summarize: Whether to summarize the result.
        for_save: Whether the result is for saving.
        
        Returns:
        A resolved expression with the appropriate output field.
        
        Raises:
        ValueError: If the output field is not a DateField, TimeField, or DateTimeField.
        ValueError: If the
        """

        copy = super().resolve_expression(query, allow_joins, reuse, summarize, for_save)
        field = copy.lhs.output_field
        # DateTimeField is a subclass of DateField so this works for both.
        assert isinstance(field, (DateField, TimeField)), (
            "%r isn't a DateField, TimeField, or DateTimeField." % field.name
        )
        # If self.output_field was None, then accessing the field will trigger
        # the resolver to assign it to self.lhs.output_field.
        if not isinstance(copy.output_field, (DateField, DateTimeField, TimeField)):
            raise ValueError('output_field must be either DateField, TimeField, or DateTimeField')
        # Passing dates or times to functions expecting datetimes is most
        # likely a mistake.
        class_output_field = self.__class__.output_field if isinstance(self.__class__.output_field, Field) else None
        output_field = class_output_field or copy.output_field
        has_explicit_output_field = class_output_field or field.__class__ is not copy.output_field.__class__
        if type(field) == DateField and (
                isinstance(output_field, DateTimeField) or copy.kind in ('hour', 'minute', 'second', 'time')):
            raise ValueError("Cannot truncate DateField '%s' to %s. " % (
                field.name, output_field.__class__.__name__ if has_explicit_output_field else 'DateTimeField'
            ))
        elif isinstance(field, TimeField) and (
                isinstance(output_field, DateTimeField) or
                copy.kind in ('year', 'quarter', 'month', 'week', 'day', 'date')):
            raise ValueError("Cannot truncate TimeField '%s' to %s. " % (
                field.name, output_field.__class__.__name__ if has_explicit_output_field else 'DateTimeField'
            ))
        return copy

    def convert_value(self, value, expression, connection):
        """
        Converts a given value based on the output field type and database settings.
        
        Args:
        value (datetime): The value to be converted.
        expression (ExpressionNode): The expression node representing the field.
        connection (Connection): The database connection object.
        
        Returns:
        datetime: The converted value.
        
        Notes:
        - If the output field is a `DateTimeField`, the function adjusts the timezone of the value based on the database settings.
        - If the value is a `datetime
        """

        if isinstance(self.output_field, DateTimeField):
            if not settings.USE_TZ:
                pass
            elif value is not None:
                value = value.replace(tzinfo=None)
                value = timezone.make_aware(value, self.tzinfo, is_dst=self.is_dst)
            elif not connection.features.has_zoneinfo_database:
                raise ValueError(
                    'Database returned an invalid datetime value. Are time '
                    'zone definitions for your database installed?'
                )
        elif isinstance(value, datetime):
            if value is None:
                pass
            elif isinstance(self.output_field, DateField):
                value = value.date()
            elif isinstance(self.output_field, TimeField):
                value = value.time()
        return value


class Trunc(TruncBase):

    def __init__(self, expression, kind, output_field=None, tzinfo=None, is_dst=None, **extra):
        """
        Initialize a timezone-aware datetime field.
        
        Args:
        expression (str): The expression to be evaluated.
        kind (str): The kind of timezone information.
        output_field (Field, optional): The output field type. Defaults to None.
        tzinfo (datetime.tzinfo, optional): The timezone information. Defaults to None.
        is_dst (bool, optional): Whether daylight saving time is in effect. Defaults to None.
        **extra: Additional keyword arguments.
        
        Returns:
        """

        self.kind = kind
        super().__init__(
            expression, output_field=output_field, tzinfo=tzinfo,
            is_dst=is_dst, **extra
        )


class TruncYear(TruncBase):
    kind = 'year'


class TruncQuarter(TruncBase):
    kind = 'quarter'


class TruncMonth(TruncBase):
    kind = 'month'


class TruncWeek(TruncBase):
    """Truncate to midnight on the Monday of the week."""
    kind = 'week'


class TruncDay(TruncBase):
    kind = 'day'


class TruncDate(TruncBase):
    kind = 'date'
    lookup_name = 'date'
    output_field = DateField()

    def as_sql(self, compiler, connection):
        """
        Generates SQL for casting a datetime expression to a date.
        
        Args:
        compiler (Compiler): The database query compiler instance.
        connection (Connection): The database connection object.
        
        Returns:
        tuple: A tuple containing the generated SQL statement and the parameters to be used in the SQL statement.
        
        Important Functions:
        - `compiler.compile(self.lhs)`: Compiles the left-hand side of the expression.
        - `timezone.get_current_timezone_name()`: Retrieves the current timezone name if
        """

        # Cast to date rather than truncate to date.
        lhs, lhs_params = compiler.compile(self.lhs)
        tzname = timezone.get_current_timezone_name() if settings.USE_TZ else None
        sql = connection.ops.datetime_cast_date_sql(lhs, tzname)
        return sql, lhs_params


class TruncTime(TruncBase):
    kind = 'time'
    lookup_name = 'time'
    output_field = TimeField()

    def as_sql(self, compiler, connection):
        """
        Generates SQL for casting a datetime expression to a time.
        
        Args:
        compiler (Compiler): The database query compiler instance.
        connection (Connection): The database connection object.
        
        Returns:
        tuple: A tuple containing the generated SQL statement and a list of parameters.
        
        Important Functions:
        - `compiler.compile(self.lhs)`: Compiles the left-hand side of the expression.
        - `timezone.get_current_timezone_name()`: Retrieves the current timezone name if timezone support is enabled.
        """

        # Cast to time rather than truncate to time.
        lhs, lhs_params = compiler.compile(self.lhs)
        tzname = timezone.get_current_timezone_name() if settings.USE_TZ else None
        sql = connection.ops.datetime_cast_time_sql(lhs, tzname)
        return sql, lhs_params


class TruncHour(TruncBase):
    kind = 'hour'


class TruncMinute(TruncBase):
    kind = 'minute'


class TruncSecond(TruncBase):
    kind = 'second'


DateTimeField.register_lookup(TruncDate)
DateTimeField.register_lookup(TruncTime)
