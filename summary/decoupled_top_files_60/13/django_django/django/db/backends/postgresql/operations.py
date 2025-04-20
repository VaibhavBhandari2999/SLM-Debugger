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
        Extracts a specific part of a date or time from a given field in a SQL query.
        
        This function is designed to be used within SQL queries to extract a particular component of a date or time field. It supports extracting the day of the week, ISO year, and any other part of the date or time specified by the `lookup_type` parameter.
        
        Parameters:
        lookup_type (str): The type of date or time component to extract. Supported values include 'week_day', 'iso_year',
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
        Converts a field to a timezone-aware SQL expression.
        
        This function modifies the provided field name to include a timezone conversion
        if timezone support is enabled in the settings.
        
        Parameters:
        field_name (str): The name of the field to be converted.
        tzname (str): The target timezone name.
        
        Returns:
        str: The modified SQL field name with timezone conversion if USE_TZ is True.
        
        Note:
        If settings.USE_TZ is False, the original field name is returned unchanged
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
        if name.startswith('"') and name.endswith('"'):
            return name  # Quoting once is enough.
        return '"%s"' % name

    def set_time_zone_sql(self):
        return "SET TIME ZONE %s"

    def sql_flush(self, style, tables, sequences, allow_cascade=False):
        """
        Flushes the database tables and sequences.
        
        This function is used to truncate specified tables and reset their sequences. It accepts a style object for SQL formatting, a list of tables to truncate, a list of sequences to reset, and an optional boolean flag to allow cascading deletes.
        
        Parameters:
        style (Style): An object for formatting SQL statements.
        tables (list): A list of table names to be truncated.
        sequences (list): A list of sequence names to be reset.
        allow_c
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
        Generates SQL statements to reset sequence indices for specified sequences.
        
        This function takes a database style object and a list of sequence information dictionaries. Each dictionary contains the table name and column name for a sequence. The function returns a list of SQL statements to reset the sequence indices to 1.
        
        Parameters:
        - style: A database style object that provides SQL formatting methods.
        - sequences: A list of dictionaries, where each dictionary contains:
        - 'table': The name of the table containing the sequence.
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
        if inline:
            return "USING INDEX TABLESPACE %s" % self.quote_name(tablespace)
        else:
            return "TABLESPACE %s" % self.quote_name(tablespace)

    def sequence_reset_sql(self, style, model_list):
        """
        Reset the sequence of auto-incrementing fields for the given models.
        
        This function generates SQL statements to reset the sequences of auto-incrementing fields for the specified models in a Django application. The sequences are reset to the maximum value of the primary key (if any records exist) or to 1 if no records exist.
        
        Parameters:
        style (Style): An instance of the Django `Style` class used for SQL formatting.
        model_list (list): A list of Django model classes for which
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
        if fields:
            params = [param for param_list in params for param in param_list]
            return (['DISTINCT ON (%s)' % ', '.join(fields)], params)
        else:
            return ['DISTINCT'], []

    def last_executed_query(self, cursor, sql, params):
        # http://initd.org/psycopg/docs/cursor.html#cursor.query
        # The query attribute is a Psycopg extension to the DB API 2.0.
        if cursor.query is not None:
            return cursor.query.decode()
        return None

    def return_insert_id(self):
        return "RETURNING %s", ()

    def bulk_insert_sql(self, fields, placeholder_rows):
        """
        Generates a SQL 'VALUES' clause for bulk insert operations.
        
        This function constructs a SQL 'VALUES' clause for use in bulk insert operations. It takes a list of field names and a list of placeholder rows.
        
        Parameters:
        fields (list): A list of field names as strings.
        placeholder_rows (list of tuples): A list of tuples, where each tuple represents a row of placeholders for the values.
        
        Returns:
        str: A string representing the SQL 'VALUES' clause for the bulk
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
        if value:
            return Inet(value)
        return None

    def subtract_temporals(self, internal_type, lhs, rhs):
        """
        Subtracts two temporal values and returns the difference in days.
        
        This method is used to calculate the difference between two temporal values, typically dates, and returns the result as an interval in days.
        
        Parameters:
        internal_type (str): The type of the temporal field, e.g., 'DateField'.
        lhs (tuple): A tuple containing the SQL representation and parameters for the left-hand side temporal value.
        rhs (tuple): A tuple containing the SQL representation and parameters for the right-hand side temporal
        """

        if internal_type == 'DateField':
            lhs_sql, lhs_params = lhs
            rhs_sql, rhs_params = rhs
            return "(interval '1 day' * (%s - %s))" % (lhs_sql, rhs_sql), lhs_params + rhs_params
        return super().subtract_temporals(internal_type, lhs, rhs)

    def window_frame_range_start_end(self, start=None, end=None):
        start_, end_ = super().window_frame_range_start_end(start, end)
        if (start and start < 0) or (end and end > 0):
            raise NotSupportedError(
                'PostgreSQL only supports UNBOUNDED together with PRECEDING '
                'and FOLLOWING.'
            )
        return start_, end_

    def explain_query_prefix(self, format=None, **options):
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
s:
            extra.update({
                name.upper(): 'true' if value else 'false'
                for name, value in options.items()
            })
        if extra:
            prefix += ' (%s)' % ', '.join('%s %s' % i for i in extra.items())
        return prefix

    def ignore_conflicts_suffix_sql(self, ignore_conflicts=None):
        return 'ON CONFLICT DO NOTHING' if ignore_conflicts else super().ignore_conflicts_suffix_sql(ignore_conflicts)
