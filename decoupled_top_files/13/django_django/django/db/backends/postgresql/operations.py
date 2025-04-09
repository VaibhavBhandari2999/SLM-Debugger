from psycopg2.extras import Inet

from django.conf import settings
from django.db import NotSupportedError
from django.db.backends.base.operations import BaseDatabaseOperations


class DatabaseOperations(BaseDatabaseOperations):
    cast_char_field_without_max_length = 'varchar'
    explain_prefix = 'EXPLAIN'
    cast_data_types = {
        'AutoField': 'integer',
        'BigAutoField': 'bigint',
    }

    def unification_cast_sql(self, output_field):
        """
        Casts an output field to a specific SQL type based on its internal type.
        
        Args:
        output_field (Field): The output field to be casted.
        
        Returns:
        str: The SQL cast expression or the original field type.
        
        Notes:
        - This function handles casting for `GenericIPAddressField`, `IPAddressField`, `TimeField`, and `UUIDField`.
        - For these fields, it explicitly casts the value to the appropriate type to avoid implicit casting issues in PostgreSQL.
        """

        internal_type = output_field.get_internal_type()
        if internal_type in ("GenericIPAddressField", "IPAddressField", "TimeField", "UUIDField"):
            # PostgreSQL will resolve a union as type 'text' if input types are
            # 'unknown'.
            # https://www.postgresql.org/docs/current/static/typeconv-union-case.html
            # These fields cannot be implicitly cast back in the default
            # PostgreSQL configuration so we need to explicitly cast them.
            # We must also remove components of the type within brackets:
            # varchar(255) -> varchar.
            return 'CAST(%%s AS %s)' % output_field.db_type(self.connection).split('(')[0]
        return '%s'

    def date_extract_sql(self, lookup_type, field_name):
        """
        Extracts a specific part of a date or time from a given field using SQL.
        
        Args:
        lookup_type (str): The type of date or time part to extract. Supported types include 'week_day', 'iso_year', and any other valid PostgreSQL EXTRACT keyword.
        field_name (str): The name of the field from which to extract the date or time part.
        
        Returns:
        str: A string representing the SQL query to extract the specified date or time part.
        
        Notes
        """

        # https://www.postgresql.org/docs/current/static/functions-datetime.html#FUNCTIONS-DATETIME-EXTRACT
        if lookup_type == 'week_day':
            # For consistency across backends, we return Sunday=1, Saturday=7.
            return "EXTRACT('dow' FROM %s) + 1" % field_name
        elif lookup_type == 'iso_year':
            return "EXTRACT('isoyear' FROM %s)" % field_name
        else:
            return "EXTRACT('%s' FROM %s)" % (lookup_type, field_name)

    def date_trunc_sql(self, lookup_type, field_name):
        # https://www.postgresql.org/docs/current/static/functions-datetime.html#FUNCTIONS-DATETIME-TRUNC
        return "DATE_TRUNC('%s', %s)" % (lookup_type, field_name)

    def _convert_field_to_tz(self, field_name, tzname):
        """
        Converts a field to a timezone-aware SQL query.
        
        Args:
        field_name (str): The name of the field to be converted.
        tzname (str): The target timezone name.
        
        Returns:
        str: The modified SQL query with timezone conversion applied.
        
        Notes:
        - This function is only active when `settings.USE_TZ` is set to True.
        - It appends 'AT TIME ZONE' clause to the field name with the specified timezone name.
        """

        if settings.USE_TZ:
            field_name = "%s AT TIME ZONE '%s'" % (field_name, tzname)
        return field_name

    def datetime_cast_date_sql(self, field_name, tzname):
        field_name = self._convert_field_to_tz(field_name, tzname)
        return '(%s)::date' % field_name

    def datetime_cast_time_sql(self, field_name, tzname):
        field_name = self._convert_field_to_tz(field_name, tzname)
        return '(%s)::time' % field_name

    def datetime_extract_sql(self, lookup_type, field_name, tzname):
        field_name = self._convert_field_to_tz(field_name, tzname)
        return self.date_extract_sql(lookup_type, field_name)

    def datetime_trunc_sql(self, lookup_type, field_name, tzname):
        """
        Truncates a datetime field to a specified type using PostgreSQL's DATE_TRUNC function.
        
        Args:
        lookup_type (str): The granularity of truncation, e.g., 'year', 'month', 'day'.
        field_name (str): The name of the datetime field to be truncated.
        tzname (str): The timezone of the datetime field.
        
        Returns:
        str: A SQL query string that truncates the datetime field to the specified type.
        
        Note:
        - The
        """

        field_name = self._convert_field_to_tz(field_name, tzname)
        # https://www.postgresql.org/docs/current/static/functions-datetime.html#FUNCTIONS-DATETIME-TRUNC
        return "DATE_TRUNC('%s', %s)" % (lookup_type, field_name)

    def time_trunc_sql(self, lookup_type, field_name):
        return "DATE_TRUNC('%s', %s)::time" % (lookup_type, field_name)

    def deferrable_sql(self):
        return " DEFERRABLE INITIALLY DEFERRED"

    def fetch_returned_insert_ids(self, cursor):
        """
        Given a cursor object that has just performed an INSERT...RETURNING
        statement into a table that has an auto-incrementing ID, return the
        list of newly created IDs.
        """
        return [item[0] for item in cursor.fetchall()]

    def lookup_cast(self, lookup_type, internal_type=None):
        """
        Generates a SQL lookup clause based on the given `lookup_type` and `internal_type`.
        
        Args:
        lookup_type (str): The type of lookup to be performed, such as 'iexact', 'contains', etc.
        internal_type (str, optional): The internal type of the field being looked up, such as 'IPAddressField', 'CICharField', etc.
        
        Returns:
        str: A formatted SQL lookup clause.
        
        Notes:
        - The function casts certain text
        """

        lookup = '%s'

        # Cast text lookups to text to allow things like filter(x__contains=4)
        if lookup_type in ('iexact', 'contains', 'icontains', 'startswith',
                           'istartswith', 'endswith', 'iendswith', 'regex', 'iregex'):
            if internal_type in ('IPAddressField', 'GenericIPAddressField'):
                lookup = "HOST(%s)"
            elif internal_type in ('CICharField', 'CIEmailField', 'CITextField'):
                lookup = '%s::citext'
            else:
                lookup = "%s::text"

        # Use UPPER(x) for case-insensitive lookups; it's faster.
        if lookup_type in ('iexact', 'icontains', 'istartswith', 'iendswith'):
            lookup = 'UPPER(%s)' % lookup

        return lookup

    def no_limit_value(self):
        return None

    def prepare_sql_script(self, sql):
        return [sql]

    def quote_name(self, name):
        """
        Generate a quoted SQL identifier.
        
        This function takes a string `name` as input and returns a quoted SQL identifier. If the input `name` already starts and ends with double quotes ("), it is returned as is. Otherwise, the function wraps the `name` in double quotes.
        
        Args:
        name (str): The input string representing an SQL identifier.
        
        Returns:
        str: A quoted SQL identifier, either the original `name` if it was already quoted, or the `
        """

        if name.startswith('"') and name.endswith('"'):
            return name  # Quoting once is enough.
        return '"%s"' % name

    def set_time_zone_sql(self):
        return "SET TIME ZONE %s"

    def sql_flush(self, style, tables, sequences, allow_cascade=False):
        """
        Flushes the contents of the specified tables and resets their sequences.
        
        Args:
        style (Style): The database-specific SQL style.
        tables (List[str]): A list of table names to be truncated.
        sequences (List[str]): A list of sequence names to be reset.
        allow_cascade (bool, optional): Whether to allow cascading deletes during truncation. Defaults to False.
        
        Returns:
        List[str]: A list of SQL statements to flush the tables and reset sequences.
        """

        if tables:
            # Perform a single SQL 'TRUNCATE x, y, z...;' statement.  It allows
            # us to truncate tables referenced by a foreign key in any other
            # table.
            tables_sql = ', '.join(
                style.SQL_FIELD(self.quote_name(table)) for table in tables)
            if allow_cascade:
                sql = ['%s %s %s;' % (
                    style.SQL_KEYWORD('TRUNCATE'),
                    tables_sql,
                    style.SQL_KEYWORD('CASCADE'),
                )]
            else:
                sql = ['%s %s;' % (
                    style.SQL_KEYWORD('TRUNCATE'),
                    tables_sql,
                )]
            sql.extend(self.sequence_reset_by_name_sql(style, sequences))
            return sql
        else:
            return []

    def sequence_reset_by_name_sql(self, style, sequences):
        """
        Generates SQL statements to reset sequence indices for given tables and columns.
        
        Args:
        style (Style): The SQL style object used to format the generated SQL.
        sequences (list): A list of dictionaries containing information about the sequences to be reset. Each dictionary should have keys 'table' and 'column'.
        
        Returns:
        list: A list of SQL statements to reset the sequence indices.
        """

        # 'ALTER SEQUENCE sequence_name RESTART WITH 1;'... style SQL statements
        # to reset sequence indices
        sql = []
        for sequence_info in sequences:
            table_name = sequence_info['table']
            # 'id' will be the case if it's an m2m using an autogenerated
            # intermediate table (see BaseDatabaseIntrospection.sequence_list).
            column_name = sequence_info['column'] or 'id'
            sql.append("%s setval(pg_get_serial_sequence('%s','%s'), 1, false);" % (
                style.SQL_KEYWORD('SELECT'),
                style.SQL_TABLE(self.quote_name(table_name)),
                style.SQL_FIELD(column_name),
            ))
        return sql

    def tablespace_sql(self, tablespace, inline=False):
        """
        Generates SQL for specifying a tablespace.
        
        Args:
        tablespace (str): The name of the tablespace to be used.
        inline (bool, optional): If True, the tablespace is specified inline with the index. Defaults to False.
        
        Returns:
        str: The generated SQL statement for specifying the tablespace.
        """

        if inline:
            return "USING INDEX TABLESPACE %s" % self.quote_name(tablespace)
        else:
            return "TABLESPACE %s" % self.quote_name(tablespace)

    def sequence_reset_sql(self, style, model_list):
        """
        Resets the sequences of specified models' primary keys and many-to-many relationships.
        
        Args:
        style: The SQL style object used for formatting.
        model_list: A list of Django model classes.
        
        Returns:
        A list of SQL statements to reset sequences.
        """

        from django.db import models
        output = []
        qn = self.quote_name
        for model in model_list:
            # Use `coalesce` to set the sequence for each model to the max pk value if there are records,
            # or 1 if there are none. Set the `is_called` property (the third argument to `setval`) to true
            # if there are records (as the max pk value is already in use), otherwise set it to false.
            # Use pg_get_serial_sequence to get the underlying sequence name from the table name
            # and column name (available since PostgreSQL 8)

            for f in model._meta.local_fields:
                if isinstance(f, models.AutoField):
                    output.append(
                        "%s setval(pg_get_serial_sequence('%s','%s'), "
                        "coalesce(max(%s), 1), max(%s) %s null) %s %s;" % (
                            style.SQL_KEYWORD('SELECT'),
                            style.SQL_TABLE(qn(model._meta.db_table)),
                            style.SQL_FIELD(f.column),
                            style.SQL_FIELD(qn(f.column)),
                            style.SQL_FIELD(qn(f.column)),
                            style.SQL_KEYWORD('IS NOT'),
                            style.SQL_KEYWORD('FROM'),
                            style.SQL_TABLE(qn(model._meta.db_table)),
                        )
                    )
                    break  # Only one AutoField is allowed per model, so don't bother continuing.
            for f in model._meta.many_to_many:
                if not f.remote_field.through:
                    output.append(
                        "%s setval(pg_get_serial_sequence('%s','%s'), "
                        "coalesce(max(%s), 1), max(%s) %s null) %s %s;" % (
                            style.SQL_KEYWORD('SELECT'),
                            style.SQL_TABLE(qn(f.m2m_db_table())),
                            style.SQL_FIELD('id'),
                            style.SQL_FIELD(qn('id')),
                            style.SQL_FIELD(qn('id')),
                            style.SQL_KEYWORD('IS NOT'),
                            style.SQL_KEYWORD('FROM'),
                            style.SQL_TABLE(qn(f.m2m_db_table()))
                        )
                    )
        return output

    def prep_for_iexact_query(self, x):
        return x

    def max_name_length(self):
        """
        Return the maximum length of an identifier.

        The maximum length of an identifier is 63 by default, but can be
        changed by recompiling PostgreSQL after editing the NAMEDATALEN
        macro in src/include/pg_config_manual.h.

        This implementation returns 63, but can be overridden by a custom
        database backend that inherits most of its behavior from this one.
        """
        return 63

    def distinct_sql(self, fields, params):
        """
        Generates a SQL DISTINCT query clause.
        
        Args:
        fields (List[str]): The fields to apply the DISTINCT constraint on.
        params (List[List[Any]]): A list of parameter lists, where each sublist contains parameters corresponding to the fields.
        
        Returns:
        Tuple[List[str], List[Any]]: A tuple containing the SQL DISTINCT clause and the flattened list of parameters.
        
        If `fields` is not empty, it returns a 'DISTINCT ON' clause with the specified fields and the
        """

        if fields:
            params = [param for param_list in params for param in param_list]
            return (['DISTINCT ON (%s)' % ', '.join(fields)], params)
        else:
            return ['DISTINCT'], []

    def last_executed_query(self, cursor, sql, params):
        """
        Retrieve the last executed SQL query.
        
        Args:
        cursor (psycopg2.extensions.cursor): A database cursor object.
        sql (str): The SQL query string.
        params (tuple): Parameters for the SQL query.
        
        Returns:
        str: The decoded last executed SQL query or None if no query was found.
        """

        # http://initd.org/psycopg/docs/cursor.html#cursor.query
        # The query attribute is a Psycopg extension to the DB API 2.0.
        if cursor.query is not None:
            return cursor.query.decode()
        return None

    def return_insert_id(self):
        return "RETURNING %s", ()

    def bulk_insert_sql(self, fields, placeholder_rows):
        """
        Generates SQL for bulk inserting multiple rows into a database.
        
        Args:
        fields (list): A list of field names.
        placeholder_rows (list): A list of tuples containing placeholder values for each row.
        
        Returns:
        str: The generated SQL statement for bulk insertion.
        
        This function takes a list of field names and a list of tuples representing placeholder rows. It constructs an SQL statement with placeholders for the values and returns the resulting SQL string.
        """

        placeholder_rows_sql = (", ".join(row) for row in placeholder_rows)
        values_sql = ", ".join("(%s)" % sql for sql in placeholder_rows_sql)
        return "VALUES " + values_sql

    def adapt_datefield_value(self, value):
        return value

    def adapt_datetimefield_value(self, value):
        return value

    def adapt_timefield_value(self, value):
        return value

    def adapt_ipaddressfield_value(self, value):
        """
        Adapt an IP address field value.
        
        Args:
        value (str): The IP address value to be adapted.
        
        Returns:
        Inet: An adapted IP address object if the input value is not empty; otherwise, returns None.
        """

        if value:
            return Inet(value)
        return None

    def subtract_temporals(self, internal_type, lhs, rhs):
        """
        Subtracts two temporals of the specified type.
        
        Args:
        internal_type (str): The type of the temporals ('DateField').
        lhs: The left-hand side temporal value, represented as a tuple containing SQL representation and parameters.
        rhs: The right-hand side temporal value, represented as a tuple containing SQL representation and parameters.
        
        Returns:
        A tuple containing the SQL representation of the subtraction result and the combined parameters list.
        """

        if internal_type == 'DateField':
            lhs_sql, lhs_params = lhs
            rhs_sql, rhs_params = rhs
            return "(interval '1 day' * (%s - %s))" % (lhs_sql, rhs_sql), lhs_params + rhs_params
        return super().subtract_temporals(internal_type, lhs, rhs)

    def window_frame_range_start_end(self, start=None, end=None):
        """
        Generates a window frame range based on the specified start and end positions.
        
        Args:
        start (int, optional): The starting position of the window frame. If negative, raises an error.
        end (int, optional): The ending position of the window frame. If positive, raises an error.
        
        Returns:
        tuple: A tuple containing the adjusted start and end positions of the window frame.
        
        Raises:
        NotSupportedError: If `start` is negative or `end`
        """

        start_, end_ = super().window_frame_range_start_end(start, end)
        if (start and start < 0) or (end and end > 0):
            raise NotSupportedError(
                'PostgreSQL only supports UNBOUNDED together with PRECEDING '
                'and FOLLOWING.'
            )
        return start_, end_

    def explain_query_prefix(self, format=None, **options):
        """
        Generates an explanation prefix for a query based on the provided format and options.
        
        Args:
        format (str, optional): The format of the query. If specified, it will be included in the prefix.
        options (dict): A dictionary of options that can be used to customize the query. Each option is converted to uppercase and its value is set to 'true' or 'false'.
        
        Returns:
        str: The generated prefix string with the format and options included.
        """

        prefix = super().explain_query_prefix(format)
        extra = {}
        if format:
            extra['FORMAT'] = format
        if options:
            extra.update({
                name.upper(): 'true' if value else 'false'
                for name, value in options.items()
            })
        if extra:
            prefix += ' (%s)' % ', '.join('%s %s' % i for i in extra.items())
        return prefix

    def ignore_conflicts_suffix_sql(self, ignore_conflicts=None):
        return 'ON CONFLICT DO NOTHING' if ignore_conflicts else super().ignore_conflicts_suffix_sql(ignore_conflicts)
