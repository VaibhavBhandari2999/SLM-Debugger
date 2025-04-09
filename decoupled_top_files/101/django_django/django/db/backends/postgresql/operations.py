from psycopg2.extras import Inet

from django.conf import settings
from django.db.backends.base.operations import BaseDatabaseOperations
from django.db.backends.utils import split_tzname_delta
from django.db.models.constants import OnConflict


class DatabaseOperations(BaseDatabaseOperations):
    cast_char_field_without_max_length = "varchar"
    explain_prefix = "EXPLAIN"
    explain_options = frozenset(
        [
            "ANALYZE",
            "BUFFERS",
            "COSTS",
            "SETTINGS",
            "SUMMARY",
            "TIMING",
            "VERBOSE",
            "WAL",
        ]
    )
    cast_data_types = {
        "AutoField": "integer",
        "BigAutoField": "bigint",
        "SmallAutoField": "smallint",
    }

    def unification_cast_sql(self, output_field):
        """
        Casts the output field to a specific SQL type based on its internal type.
        
        Args:
        output_field (Field): The output field to be casted.
        
        Returns:
        str: The SQL cast expression.
        
        Notes:
        - This function is used to ensure that certain fields are correctly casted to their respective SQL types when performing UNION operations.
        - It handles fields such as `GenericIPAddressField`, `IPAddressField`, `TimeField`, and `UUIDField`.
        - For
        """

        internal_type = output_field.get_internal_type()
        if internal_type in (
            "GenericIPAddressField",
            "IPAddressField",
            "TimeField",
            "UUIDField",
        ):
            # PostgreSQL will resolve a union as type 'text' if input types are
            # 'unknown'.
            # https://www.postgresql.org/docs/current/typeconv-union-case.html
            # These fields cannot be implicitly cast back in the default
            # PostgreSQL configuration so we need to explicitly cast them.
            # We must also remove components of the type within brackets:
            # varchar(255) -> varchar.
            return (
                "CAST(%%s AS %s)" % output_field.db_type(self.connection).split("(")[0]
            )
        return "%s"

    def date_extract_sql(self, lookup_type, sql, params):
        """
        Extracts a specific part of a date or time from a SQL query.
        
        Args:
        lookup_type (str): The type of date part to extract, such as 'week_day', 'iso_week_day', or 'iso_year'.
        sql (str): The SQL query containing the date or timestamp expression.
        params (tuple): Additional parameters required by the SQL query.
        
        Returns:
        tuple: A tuple containing the SQL extract statement and a tuple of parameters.
        
        Notes:
        -
        """

        # https://www.postgresql.org/docs/current/functions-datetime.html#FUNCTIONS-DATETIME-EXTRACT
        extract_sql = f"EXTRACT(%s FROM {sql})"
        extract_param = lookup_type
        if lookup_type == "week_day":
            # For consistency across backends, we return Sunday=1, Saturday=7.
            extract_sql = f"EXTRACT(%s FROM {sql}) + 1"
            extract_param = "dow"
        elif lookup_type == "iso_week_day":
            extract_param = "isodow"
        elif lookup_type == "iso_year":
            extract_param = "isoyear"
        return extract_sql, (extract_param, *params)

    def date_trunc_sql(self, lookup_type, sql, params, tzname=None):
        """
        Truncates a datetime value to a specified unit using PostgreSQL's DATE_TRUNC function.
        
        Args:
        lookup_type (str): The unit to truncate the datetime value to, e.g., 'year', 'month', 'day'.
        sql (str): The SQL query or expression representing the datetime value.
        params (tuple): Additional parameters required by the SQL query or expression.
        tzname (str, optional): The timezone name to convert the datetime value to before truncation. Defaults to
        """

        sql, params = self._convert_sql_to_tz(sql, params, tzname)
        # https://www.postgresql.org/docs/current/functions-datetime.html#FUNCTIONS-DATETIME-TRUNC
        return f"DATE_TRUNC(%s, {sql})", (lookup_type, *params)

    def _prepare_tzname_delta(self, tzname):
        """
        Prepares a timezone name with an optional delta.
        
        This function takes a timezone name and optionally processes any attached
        time delta (e.g., '+02:00' or '-05:30'). It splits the timezone name into
        its components, applies the sign of the delta to the offset, and returns
        the formatted timezone name with the adjusted offset.
        
        Args:
        tzname (str): The timezone name to be processed.
        
        Returns:
        """

        tzname, sign, offset = split_tzname_delta(tzname)
        if offset:
            sign = "-" if sign == "+" else "+"
            return f"{tzname}{sign}{offset}"
        return tzname

    def _convert_sql_to_tz(self, sql, params, tzname):
        """
        Converts SQL query to timezone-aware format.
        
        Args:
        sql (str): The original SQL query.
        params (tuple): Parameters to be used in the SQL query.
        tzname (str): Timezone name to convert the query to.
        
        Returns:
        tuple: A tuple containing the modified SQL query and updated parameters.
        
        Notes:
        - If `settings.USE_TZ` is True and a `tzname` is provided, the function will modify the SQL query
        """

        if tzname and settings.USE_TZ:
            tzname_param = self._prepare_tzname_delta(tzname)
            return f"{sql} AT TIME ZONE %s", (*params, tzname_param)
        return sql, params

    def datetime_cast_date_sql(self, sql, params, tzname):
        sql, params = self._convert_sql_to_tz(sql, params, tzname)
        return f"({sql})::date", params

    def datetime_cast_time_sql(self, sql, params, tzname):
        sql, params = self._convert_sql_to_tz(sql, params, tzname)
        return f"({sql})::time", params

    def datetime_extract_sql(self, lookup_type, sql, params, tzname):
        """
        Extracts a specific datetime component from a SQL query based on the given lookup type.
        
        Args:
        lookup_type (str): The type of datetime component to extract, such as 'second'.
        sql (str): The original SQL query.
        params (tuple): Parameters to be used in the SQL query.
        tzname (str): The timezone name to convert the datetime to.
        
        Returns:
        tuple: A tuple containing the modified SQL query and the updated parameters.
        
        Important Functions:
        """

        sql, params = self._convert_sql_to_tz(sql, params, tzname)
        if lookup_type == "second":
            # Truncate fractional seconds.
            return (
                f"EXTRACT(%s FROM DATE_TRUNC(%s, {sql}))",
                ("second", "second", *params),
            )
        return self.date_extract_sql(lookup_type, sql, params)

    def datetime_trunc_sql(self, lookup_type, sql, params, tzname):
        """
        Truncates a datetime value to a specified unit within a given SQL query.
        
        Args:
        lookup_type (str): The unit to truncate the datetime value to (e.g., 'day', 'hour').
        sql (str): The original SQL query containing the datetime expression.
        params (tuple): Parameters associated with the SQL query.
        tzname (str): Timezone name to convert the datetime to before truncation.
        
        Returns:
        tuple: A tuple containing the modified SQL query
        """

        sql, params = self._convert_sql_to_tz(sql, params, tzname)
        # https://www.postgresql.org/docs/current/functions-datetime.html#FUNCTIONS-DATETIME-TRUNC
        return f"DATE_TRUNC(%s, {sql})", (lookup_type, *params)

    def time_extract_sql(self, lookup_type, sql, params):
        """
        Extracts the specified time component from a SQL query result.
        
        Args:
        lookup_type (str): The type of time component to extract, such as 'second'.
        sql (str): The SQL query to be executed.
        params (tuple): Parameters to be passed to the SQL query.
        
        Returns:
        tuple: A tuple containing the SQL expression for extracting the time component and the corresponding parameters.
        
        Notes:
        - If `lookup_type` is 'second', the function truncates
        """

        if lookup_type == "second":
            # Truncate fractional seconds.
            return (
                f"EXTRACT(%s FROM DATE_TRUNC(%s, {sql}))",
                ("second", "second", *params),
            )
        return self.date_extract_sql(lookup_type, sql, params)

    def time_trunc_sql(self, lookup_type, sql, params, tzname=None):
        sql, params = self._convert_sql_to_tz(sql, params, tzname)
        return f"DATE_TRUNC(%s, {sql})::time", (lookup_type, *params)

    def deferrable_sql(self):
        return " DEFERRABLE INITIALLY DEFERRED"

    def fetch_returned_insert_rows(self, cursor):
        """
        Given a cursor object that has just performed an INSERT...RETURNING
        statement into a table, return the tuple of returned data.
        """
        return cursor.fetchall()

    def lookup_cast(self, lookup_type, internal_type=None):
        """
        Generates a SQL lookup clause based on the given `lookup_type` and `internal_type`.
        
        Args:
        lookup_type (str): The type of lookup to be performed.
        internal_type (str, optional): The internal type of the field being looked up.
        
        Returns:
        str: A formatted SQL lookup clause.
        
        Notes:
        - This function is used to generate a SQL lookup clause that can be used in database queries.
        - It handles different types of lookups such as
        """

        lookup = "%s"

        # Cast text lookups to text to allow things like filter(x__contains=4)
        if lookup_type in (
            "iexact",
            "contains",
            "icontains",
            "startswith",
            "istartswith",
            "endswith",
            "iendswith",
            "regex",
            "iregex",
        ):
            if internal_type in ("IPAddressField", "GenericIPAddressField"):
                lookup = "HOST(%s)"
            elif internal_type in ("CICharField", "CIEmailField", "CITextField"):
                lookup = "%s::citext"
            else:
                lookup = "%s::text"

        # Use UPPER(x) for case-insensitive lookups; it's faster.
        if lookup_type in ("iexact", "icontains", "istartswith", "iendswith"):
            lookup = "UPPER(%s)" % lookup

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

    def sql_flush(self, style, tables, *, reset_sequences=False, allow_cascade=False):
        """
        Truncates specified tables in the database.
        
        Args:
        style (Style): The style object used for formatting SQL statements.
        tables (list): A list of table names to be truncated.
        reset_sequences (bool, optional): If True, resets sequences after truncation. Defaults to False.
        allow_cascade (bool, optional): If True, allows cascading deletion. Defaults to False.
        
        Returns:
        list: A list of SQL statements to be executed.
        """

        if not tables:
            return []

        # Perform a single SQL 'TRUNCATE x, y, z...;' statement. It allows us
        # to truncate tables referenced by a foreign key in any other table.
        sql_parts = [
            style.SQL_KEYWORD("TRUNCATE"),
            ", ".join(style.SQL_FIELD(self.quote_name(table)) for table in tables),
        ]
        if reset_sequences:
            sql_parts.append(style.SQL_KEYWORD("RESTART IDENTITY"))
        if allow_cascade:
            sql_parts.append(style.SQL_KEYWORD("CASCADE"))
        return ["%s;" % " ".join(sql_parts)]

    def sequence_reset_by_name_sql(self, style, sequences):
        """
        Generates SQL statements to reset sequence indices for given tables and columns.
        
        Args:
        style (Style): The SQL style object used for formatting.
        sequences (list): A list of dictionaries containing sequence information, each with keys 'table' and 'column'.
        
        Returns:
        list: A list of SQL statements to reset sequence indices.
        """

        # 'ALTER SEQUENCE sequence_name RESTART WITH 1;'... style SQL statements
        # to reset sequence indices
        sql = []
        for sequence_info in sequences:
            table_name = sequence_info["table"]
            # 'id' will be the case if it's an m2m using an autogenerated
            # intermediate table (see BaseDatabaseIntrospection.sequence_list).
            column_name = sequence_info["column"] or "id"
            sql.append(
                "%s setval(pg_get_serial_sequence('%s','%s'), 1, false);"
                % (
                    style.SQL_KEYWORD("SELECT"),
                    style.SQL_TABLE(self.quote_name(table_name)),
                    style.SQL_FIELD(column_name),
                )
            )
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
        Resets the sequences of specified models' primary keys.
        
        Args:
        style (Style): The SQL style object used for formatting.
        model_list (list): A list of Django model classes.
        
        Returns:
        list: A list of SQL statements to reset the sequences.
        
        This function iterates over a list of Django model classes, identifies the `AutoField` (primary key) of each model, and generates SQL statements to reset the corresponding sequences. It uses the `coalesce`
        """

        from django.db import models

        output = []
        qn = self.quote_name
        for model in model_list:
            # Use `coalesce` to set the sequence for each model to the max pk
            # value if there are records, or 1 if there are none. Set the
            # `is_called` property (the third argument to `setval`) to true if
            # there are records (as the max pk value is already in use),
            # otherwise set it to false. Use pg_get_serial_sequence to get the
            # underlying sequence name from the table name and column name.

            for f in model._meta.local_fields:
                if isinstance(f, models.AutoField):
                    output.append(
                        "%s setval(pg_get_serial_sequence('%s','%s'), "
                        "coalesce(max(%s), 1), max(%s) %s null) %s %s;"
                        % (
                            style.SQL_KEYWORD("SELECT"),
                            style.SQL_TABLE(qn(model._meta.db_table)),
                            style.SQL_FIELD(f.column),
                            style.SQL_FIELD(qn(f.column)),
                            style.SQL_FIELD(qn(f.column)),
                            style.SQL_KEYWORD("IS NOT"),
                            style.SQL_KEYWORD("FROM"),
                            style.SQL_TABLE(qn(model._meta.db_table)),
                        )
                    )
                    # Only one AutoField is allowed per model, so don't bother
                    # continuing.
                    break
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
        params (List[List[Any]]): The parameters associated with the fields.
        
        Returns:
        Tuple[List[str], List[Any]]: A tuple containing the SQL DISTINCT clause and the corresponding parameters.
        
        Notes:
        - If `fields` is not empty, it constructs a DISTINCT ON clause with the specified fields and flattens the parameters list.
        - If `
        """

        if fields:
            params = [param for param_list in params for param in param_list]
            return (["DISTINCT ON (%s)" % ", ".join(fields)], params)
        else:
            return ["DISTINCT"], []

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

        # https://www.psycopg.org/docs/cursor.html#cursor.query
        # The query attribute is a Psycopg extension to the DB API 2.0.
        if cursor.query is not None:
            return cursor.query.decode()
        return None

    def return_insert_columns(self, fields):
        """
        Generates a SQL RETURNING clause for inserting records.
        
        Args:
        fields (list): A list of model fields to be included in the returning clause.
        
        Returns:
        tuple: A tuple containing the generated SQL RETURNING clause and an empty tuple.
        
        Notes:
        - The function checks if the `fields` list is empty and returns an empty string and an empty tuple if it is.
        - It constructs the SQL column names using the `quote_name` method for both the table
        """

        if not fields:
            return "", ()
        columns = [
            "%s.%s"
            % (
                self.quote_name(field.model._meta.db_table),
                self.quote_name(field.column),
            )
            for field in fields
        ]
        return "RETURNING %s" % ", ".join(columns), ()

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

    def adapt_decimalfield_value(self, value, max_digits=None, decimal_places=None):
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
        internal_type (str): The type of the temporals, either "DateField".
        lhs: The left-hand side temporal value, expected to be a tuple containing SQL representation and parameters.
        rhs: The right-hand side temporal value, expected to be a tuple containing SQL representation and parameters.
        
        Returns:
        A tuple containing the SQL representation of the subtraction result and the combined parameters.
        """

        if internal_type == "DateField":
            lhs_sql, lhs_params = lhs
            rhs_sql, rhs_params = rhs
            params = (*lhs_params, *rhs_params)
            return "(interval '1 day' * (%s - %s))" % (lhs_sql, rhs_sql), params
        return super().subtract_temporals(internal_type, lhs, rhs)

    def explain_query_prefix(self, format=None, **options):
        """
        Generates an explanation prefix for a query based on the provided options.
        
        Args:
        format (str, optional): The format of the query output. Defaults to None.
        **options: Additional options to customize the query behavior.
        
        Returns:
        str: The generated query prefix with any specified options included.
        
        Keyword Arguments:
        - **options**: A dictionary of options that can be used to modify the query's behavior. These options are normalized to uppercase and converted to 'true' or
        """

        extra = {}
        # Normalize options.
        if options:
            options = {
                name.upper(): "true" if value else "false"
                for name, value in options.items()
            }
            for valid_option in self.explain_options:
                value = options.pop(valid_option, None)
                if value is not None:
                    extra[valid_option] = value
        prefix = super().explain_query_prefix(format, **options)
        if format:
            extra["FORMAT"] = format
        if extra:
            prefix += " (%s)" % ", ".join("%s %s" % i for i in extra.items())
        return prefix

    def on_conflict_suffix_sql(self, fields, on_conflict, update_fields, unique_fields):
        """
        Generates an ON CONFLICT clause for SQL insert or update operations.
        
        Args:
        fields (list): List of field names.
        on_conflict (OnConflict): The conflict resolution strategy, either `IGNORE` or `UPDATE`.
        update_fields (list): List of field names to be updated in case of a conflict.
        unique_fields (list): List of field names that are unique and used for conflict detection.
        
        Returns:
        str: The generated ON CONFLICT clause as a
        """

        if on_conflict == OnConflict.IGNORE:
            return "ON CONFLICT DO NOTHING"
        if on_conflict == OnConflict.UPDATE:
            return "ON CONFLICT(%s) DO UPDATE SET %s" % (
                ", ".join(map(self.quote_name, unique_fields)),
                ", ".join(
                    [
                        f"{field} = EXCLUDED.{field}"
                        for field in map(self.quote_name, update_fields)
                    ]
                ),
            )
        return super().on_conflict_suffix_sql(
            fields,
            on_conflict,
            update_fields,
            unique_fields,
        )
