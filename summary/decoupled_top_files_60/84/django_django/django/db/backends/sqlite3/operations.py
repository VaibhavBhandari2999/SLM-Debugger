import datetime
import decimal
import uuid
from functools import lru_cache
from itertools import chain

from django.conf import settings
from django.core.exceptions import FieldError
from django.db import DatabaseError, NotSupportedError, models
from django.db.backends.base.operations import BaseDatabaseOperations
from django.db.models.expressions import Col
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime, parse_time
from django.utils.functional import cached_property


class DatabaseOperations(BaseDatabaseOperations):
    cast_char_field_without_max_length = 'text'
    cast_data_types = {
        'DateField': 'TEXT',
        'DateTimeField': 'TEXT',
    }
    explain_prefix = 'EXPLAIN QUERY PLAN'
    # List of datatypes to that cannot be extracted with JSON_EXTRACT() on
    # SQLite. Use JSON_TYPE() instead.
    jsonfield_datatype_values = frozenset(['null', 'false', 'true'])

    def bulk_batch_size(self, fields, objs):
        """
        SQLite has a compile-time default (SQLITE_LIMIT_VARIABLE_NUMBER) of
        999 variables per query.

        If there's only a single field to insert, the limit is 500
        (SQLITE_MAX_COMPOUND_SELECT).
        """
        if len(fields) == 1:
            return 500
        elif len(fields) > 1:
            return self.connection.features.max_query_params // len(fields)
        else:
            return len(objs)

    def check_expression_support(self, expression):
        """
        Checks if an expression is supported in SQLite3.
        
        This function validates whether a given expression is supported in SQLite3. It specifically checks for the following conditions:
        
        - If the expression is an instance of `bad_aggregates` (Sum, Avg, Variance, StdDev), it further checks the output field of the subexpression. If the output field is an instance of `bad_fields` (DateField, DateTimeField, TimeField), it raises a `NotSupportedError` because SQLite3
        """

        bad_fields = (models.DateField, models.DateTimeField, models.TimeField)
        bad_aggregates = (models.Sum, models.Avg, models.Variance, models.StdDev)
        if isinstance(expression, bad_aggregates):
            for expr in expression.get_source_expressions():
                try:
                    output_field = expr.output_field
                except (AttributeError, FieldError):
                    # Not every subexpression has an output_field which is fine
                    # to ignore.
                    pass
                else:
                    if isinstance(output_field, bad_fields):
                        raise NotSupportedError(
                            'You cannot use Sum, Avg, StdDev, and Variance '
                            'aggregations on date/time fields in sqlite3 '
                            'since date/time is saved as text.'
                        )
        if (
            isinstance(expression, models.Aggregate) and
            expression.distinct and
            len(expression.source_expressions) > 1
        ):
            raise NotSupportedError(
                "SQLite doesn't support DISTINCT on aggregate functions "
                "accepting multiple arguments."
            )

    def date_extract_sql(self, lookup_type, field_name):
        """
        Support EXTRACT with a user-defined function django_date_extract()
        that's registered in connect(). Use single quotes because this is a
        string and could otherwise cause a collision with a field name.
        """
        return "django_date_extract('%s', %s)" % (lookup_type.lower(), field_name)

    def fetch_returned_insert_rows(self, cursor):
        """
        Given a cursor object that has just performed an INSERT...RETURNING
        statement into a table, return the list of returned data.
        """
        return cursor.fetchall()

    def format_for_duration_arithmetic(self, sql):
        """Do nothing since formatting is handled in the custom function."""
        return sql

    def date_trunc_sql(self, lookup_type, field_name, tzname=None):
        return "django_date_trunc('%s', %s, %s, %s)" % (
            lookup_type.lower(),
            field_name,
            *self._convert_tznames_to_sql(tzname),
        )

    def time_trunc_sql(self, lookup_type, field_name, tzname=None):
        return "django_time_trunc('%s', %s, %s, %s)" % (
            lookup_type.lower(),
            field_name,
            *self._convert_tznames_to_sql(tzname),
        )

    def _convert_tznames_to_sql(self, tzname):
        if tzname and settings.USE_TZ:
            return "'%s'" % tzname, "'%s'" % self.connection.timezone_name
        return 'NULL', 'NULL'

    def datetime_cast_date_sql(self, field_name, tzname):
        """
        Cast a datetime field to a date in a specified timezone.
        
        This function is used to cast a datetime field to a date in a specified timezone. It takes a field name and a timezone name as input parameters.
        
        Parameters:
        field_name (str): The name of the datetime field to be cast.
        tzname (str): The timezone name to which the datetime field should be cast.
        
        Returns:
        str: A SQL expression that casts the datetime field to a date in the specified timezone.
        
        Example
        """

        return 'django_datetime_cast_date(%s, %s, %s)' % (
            field_name, *self._convert_tznames_to_sql(tzname),
        )

    def datetime_cast_time_sql(self, field_name, tzname):
        return 'django_datetime_cast_time(%s, %s, %s)' % (
            field_name, *self._convert_tznames_to_sql(tzname),
        )

    def datetime_extract_sql(self, lookup_type, field_name, tzname):
        return "django_datetime_extract('%s', %s, %s, %s)" % (
            lookup_type.lower(), field_name, *self._convert_tznames_to_sql(tzname),
        )

    def datetime_trunc_sql(self, lookup_type, field_name, tzname):
        """
        Truncates a datetime field to a specified type and timezone.
        
        This function generates a SQL query for truncating a datetime field to a specified type (e.g., 'second', 'minute', 'hour', 'day') and timezone. The generated SQL uses the 'django_datetime_trunc' function, which is assumed to be a custom function available in the database backend.
        
        Parameters:
        lookup_type (str): The type of truncation to apply. Valid values are 'second', 'minute',
        """

        return "django_datetime_trunc('%s', %s, %s, %s)" % (
            lookup_type.lower(), field_name, *self._convert_tznames_to_sql(tzname),
        )

    def time_extract_sql(self, lookup_type, field_name):
        return "django_time_extract('%s', %s)" % (lookup_type.lower(), field_name)

    def pk_default_value(self):
        return "NULL"

    def _quote_params_for_last_executed_query(self, params):
        """
        Only for last_executed_query! Don't use this to execute SQL queries!
        """
        # This function is limited both by SQLITE_LIMIT_VARIABLE_NUMBER (the
        # number of parameters, default = 999) and SQLITE_MAX_COLUMN (the
        # number of return values, default = 2000). Since Python's sqlite3
        # module doesn't expose the get_limit() C API, assume the default
        # limits are in effect and split the work in batches if needed.
        BATCH_SIZE = 999
        if len(params) > BATCH_SIZE:
            results = ()
            for index in range(0, len(params), BATCH_SIZE):
                chunk = params[index:index + BATCH_SIZE]
                results += self._quote_params_for_last_executed_query(chunk)
            return results

        sql = 'SELECT ' + ', '.join(['QUOTE(?)'] * len(params))
        # Bypass Django's wrappers and use the underlying sqlite3 connection
        # to avoid logging this query - it would trigger infinite recursion.
        cursor = self.connection.connection.cursor()
        # Native sqlite3 cursors cannot be used as context managers.
        try:
            return cursor.execute(sql, params).fetchone()
        finally:
            cursor.close()

    def last_executed_query(self, cursor, sql, params):
        # Python substitutes parameters in Modules/_sqlite/cursor.c with:
        # pysqlite_statement_bind_parameters(self->statement, parameters, allow_8bit_chars);
        # Unfortunately there is no way to reach self->statement from Python,
        # so we quote and substitute parameters manually.
        if params:
            if isinstance(params, (list, tuple)):
                params = self._quote_params_for_last_executed_query(params)
            else:
                values = tuple(params.values())
                values = self._quote_params_for_last_executed_query(values)
                params = dict(zip(params, values))
            return sql % params
        # For consistency with SQLiteCursorWrapper.execute(), just return sql
        # when there are no parameters. See #13648 and #17158.
        else:
            return sql

    def quote_name(self, name):
        if name.startswith('"') and name.endswith('"'):
            return name  # Quoting once is enough.
        return '"%s"' % name

    def no_limit_value(self):
        return -1

    def __references_graph(self, table_name):
        """
        Retrieve tables that reference a given table in a SQLite database.
        
        This function queries the SQLite database to find all tables that reference
        a specified table through foreign key constraints.
        
        Parameters:
        table_name (str): The name of the table to search for references.
        
        Returns:
        list: A list of table names that reference the specified table.
        
        Notes:
        - The function uses a Common Table Expression (CTE) to build a list of
        tables that reference the given table.
        - The search
        """

        query = """
        WITH tables AS (
            SELECT %s name
            UNION
            SELECT sqlite_master.name
            FROM sqlite_master
            JOIN tables ON (sql REGEXP %s || tables.name || %s)
        ) SELECT name FROM tables;
        """
        params = (
            table_name,
            r'(?i)\s+references\s+("|\')?',
            r'("|\')?\s*\(',
        )
        with self.connection.cursor() as cursor:
            results = cursor.execute(query, params)
            return [row[0] for row in results.fetchall()]

    @cached_property
    def _references_graph(self):
        # 512 is large enough to fit the ~330 tables (as of this writing) in
        # Django's test suite.
        return lru_cache(maxsize=512)(self.__references_graph)

    def sql_flush(self, style, tables, *, reset_sequences=False, allow_cascade=False):
        if tables and allow_cascade:
            # Simulate TRUNCATE CASCADE by recursively collecting the tables
            # referencing the tables to be flushed.
            tables = set(chain.from_iterable(self._references_graph(table) for table in tables))
        sql = ['%s %s %s;' % (
            style.SQL_KEYWORD('DELETE'),
            style.SQL_KEYWORD('FROM'),
            style.SQL_FIELD(self.quote_name(table))
        ) for table in tables]
        if reset_sequences:
            sequences = [{'table': table} for table in tables]
            sql.extend(self.sequence_reset_by_name_sql(style, sequences))
        return sql

    def sequence_reset_by_name_sql(self, style, sequences):
        if not sequences:
            return []
        return [
            '%s %s %s %s = 0 %s %s %s (%s);' % (
                style.SQL_KEYWORD('UPDATE'),
                style.SQL_TABLE(self.quote_name('sqlite_sequence')),
                style.SQL_KEYWORD('SET'),
                style.SQL_FIELD(self.quote_name('seq')),
                style.SQL_KEYWORD('WHERE'),
                style.SQL_FIELD(self.quote_name('name')),
                style.SQL_KEYWORD('IN'),
                ', '.join([
                    "'%s'" % sequence_info['table'] for sequence_info in sequences
                ]),
            ),
        ]

    def adapt_datetimefield_value(self, value):
        if value is None:
            return None

        # Expression values are adapted by the database.
        if hasattr(value, 'resolve_expression'):
            return value

        # SQLite doesn't support tz-aware datetimes
        if timezone.is_aware(value):
            if settings.USE_TZ:
                value = timezone.make_naive(value, self.connection.timezone)
            else:
                raise ValueError("SQLite backend does not support timezone-aware datetimes when USE_TZ is False.")

        return str(value)

    def adapt_timefield_value(self, value):
        """
        Adapt a time field value for database storage.
        
        This function handles the adaptation of time field values for database storage, ensuring that the value is correctly formatted and compatible with the database backend. It supports both None values and Django expression objects. For SQLite, it ensures that the datetime value is timezone-naive.
        
        Parameters:
        - value: The value to be adapted. Can be None, a Django expression object, or a datetime object.
        
        Returns:
        - None if the input value is None.
        - The input
        """

        if value is None:
            return None

        # Expression values are adapted by the database.
        if hasattr(value, 'resolve_expression'):
            return value

        # SQLite doesn't support tz-aware datetimes
        if timezone.is_aware(value):
            raise ValueError("SQLite backend does not support timezone-aware times.")

        return str(value)

    def get_db_converters(self, expression):
        """
        Generate database converters for a given expression.
        
        This method extends the functionality of the superclass by adding specific converters for different field types.
        
        Parameters:
        expression (Expression): The expression for which database converters are to be generated.
        
        Returns:
        list: A list of converters to be used for database conversion.
        
        This function first calls the superclass method to get initial converters. It then checks the internal type of the output field of the expression. Depending on the field type, it appends specific converters:
        - 'DateTime
        """

        converters = super().get_db_converters(expression)
        internal_type = expression.output_field.get_internal_type()
        if internal_type == 'DateTimeField':
            converters.append(self.convert_datetimefield_value)
        elif internal_type == 'DateField':
            converters.append(self.convert_datefield_value)
        elif internal_type == 'TimeField':
            converters.append(self.convert_timefield_value)
        elif internal_type == 'DecimalField':
            converters.append(self.get_decimalfield_converter(expression))
        elif internal_type == 'UUIDField':
            converters.append(self.convert_uuidfield_value)
        elif internal_type == 'BooleanField':
            converters.append(self.convert_booleanfield_value)
        return converters

    def convert_datetimefield_value(self, value, expression, connection):
        """
        Converts a datetime field value to a Python datetime object.
        
        This function is designed to handle the conversion of datetime field values to Python datetime objects, ensuring that the datetime is timezone-aware if necessary.
        
        Parameters:
        value (datetime or str): The datetime value to be converted. Can be a datetime object or a string that can be parsed.
        expression (Expression): The expression associated with the datetime field.
        connection (Connection): The database connection object.
        
        Returns:
        datetime: A timezone-aware datetime
        """

        if value is not None:
            if not isinstance(value, datetime.datetime):
                value = parse_datetime(value)
            if settings.USE_TZ and not timezone.is_aware(value):
                value = timezone.make_aware(value, self.connection.timezone)
        return value

    def convert_datefield_value(self, value, expression, connection):
        if value is not None:
            if not isinstance(value, datetime.date):
                value = parse_date(value)
        return value

    def convert_timefield_value(self, value, expression, connection):
        if value is not None:
            if not isinstance(value, datetime.time):
                value = parse_time(value)
        return value

    def get_decimalfield_converter(self, expression):
        # SQLite stores only 15 significant digits. Digits coming from
        # float inaccuracy must be removed.
        create_decimal = decimal.Context(prec=15).create_decimal_from_float
        if isinstance(expression, Col):
            quantize_value = decimal.Decimal(1).scaleb(-expression.output_field.decimal_places)

            def converter(value, expression, connection):
                if value is not None:
                    return create_decimal(value).quantize(quantize_value, context=expression.output_field.context)
        else:
            def converter(value, expression, connection):
                if value is not None:
                    return create_decimal(value)
        return converter

    def convert_uuidfield_value(self, value, expression, connection):
        if value is not None:
            value = uuid.UUID(value)
        return value

    def convert_booleanfield_value(self, value, expression, connection):
        return bool(value) if value in (1, 0) else value

    def bulk_insert_sql(self, fields, placeholder_rows):
        return " UNION ALL ".join(
            "SELECT %s" % ", ".join(row)
            for row in placeholder_rows
        )

    def combine_expression(self, connector, sub_expressions):
        """
        Combine multiple sub-expressions into a single expression using a specified connector.
        
        Parameters:
        connector (str): The operator or connector to use for combining the sub-expressions.
        sub_expressions (list): A list of sub-expressions to be combined.
        
        Returns:
        str: A string representing the combined expression.
        
        Notes:
        - If the connector is '^', the function uses the SQLite POWER function to combine the sub-expressions.
        - If the connector is '#', the function uses the SQLite
        """

        # SQLite doesn't have a ^ operator, so use the user-defined POWER
        # function that's registered in connect().
        if connector == '^':
            return 'POWER(%s)' % ','.join(sub_expressions)
        elif connector == '#':
            return 'BITXOR(%s)' % ','.join(sub_expressions)
        return super().combine_expression(connector, sub_expressions)

    def combine_duration_expression(self, connector, sub_expressions):
        """
        Combine multiple duration expressions into a single timedelta expression.
        
        This function takes a connector (one of '+', '-', '*', '/') and a list of sub-expressions, and returns a formatted timedelta expression.
        
        Parameters:
        connector (str): The operation to perform ('+', '-', '*', '/').
        sub_expressions (list): A list of sub-expressions to combine.
        
        Returns:
        str: A formatted timedelta expression.
        
        Raises:
        DatabaseError: If the connector is not one of '+', '-', '*', '/'.
        """

        if connector not in ['+', '-', '*', '/']:
            raise DatabaseError('Invalid connector for timedelta: %s.' % connector)
        fn_params = ["'%s'" % connector] + sub_expressions
        if len(fn_params) > 3:
            raise ValueError('Too many params for timedelta operations.')
        return "django_format_dtdelta(%s)" % ', '.join(fn_params)

    def integer_field_range(self, internal_type):
        # SQLite doesn't enforce any integer constraints
        return (None, None)

    def subtract_temporals(self, internal_type, lhs, rhs):
        lhs_sql, lhs_params = lhs
        rhs_sql, rhs_params = rhs
        params = (*lhs_params, *rhs_params)
        if internal_type == 'TimeField':
            return 'django_time_diff(%s, %s)' % (lhs_sql, rhs_sql), params
        return 'django_timestamp_diff(%s, %s)' % (lhs_sql, rhs_sql), params

    def insert_statement(self, ignore_conflicts=False):
        return 'INSERT OR IGNORE INTO' if ignore_conflicts else super().insert_statement(ignore_conflicts)

    def return_insert_columns(self, fields):
        # SQLite < 3.35 doesn't support an INSERT...RETURNING statement.
        if not fields:
            return '', ()
        columns = [
            '%s.%s' % (
                self.quote_name(field.model._meta.db_table),
                self.quote_name(field.column),
            ) for field in fields
        ]
        return 'RETURNING %s' % ', '.join(columns), ()
n
