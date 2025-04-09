"""
This file customizes the `DatabaseSchemaEditor` class for PostgreSQL databases in Django. It includes methods for managing schema changes such as creating, deleting, and altering sequences, indexes, and foreign keys. The class overrides several methods from the base `BaseDatabaseSchemaEditor` class to provide PostgreSQL-specific behavior, including handling of data types, constraints, and indexes. Additionally, it provides utility methods for quoting values and generating SQL statements for schema operations. The `quote_value` method ensures that values are properly escaped and encoded for use in PostgreSQL queries. The file also includes methods for altering field types, adding and removing indexes, and handling specific PostgreSQL features like LIKE indexes and serial fields.
"""
"""
This file customizes the `DatabaseSchemaEditor` class for PostgreSQL databases in Django. It includes methods for managing schema changes such as creating, deleting, and altering sequences, indexes, and foreign keys. The class overrides several methods from the base `BaseDatabaseSchemaEditor` class to provide PostgreSQL-specific behavior, including handling of data types, constraints, and indexes. Additionally, it provides utility methods for quoting values and generating SQL statements for schema operations. The `quote_value` method ensures that values are properly escaped and encoded for use in PostgreSQL queries. The file also includes methods for altering field types, adding and removing indexes, and handling specific PostgreSQL features like LIKE indexes and serial fields. ```python
"""
"""
The provided Python file customizes the `DatabaseSchemaEditor` class for PostgreSQL databases in Django. It includes methods for managing schema changes such as creating, deleting, and altering sequences, indexes, and foreign keys. The class overrides several methods from the base `BaseDatabaseSchemaEditor` class to provide PostgreSQL-specific behavior, including handling of data types, constraints, and indexes. It also includes utility methods for quoting values and generating SQL statements for schema operations. The `quote_value` method ensures that values are properly escaped and encoded for use in PostgreSQL queries.
"""
"""
This Python file contains customizations for the `DatabaseSchemaEditor` class used in Django to manage schema changes for PostgreSQL databases. It includes methods for creating, deleting, and altering database schema elements such as sequences, indexes, and foreign keys. The class overrides several methods from the base `BaseDatabaseSchemaEditor` class to provide PostgreSQL-specific behavior, including handling of data types, constraints, and indexes. Additionally, it provides utility methods for quoting values and generating SQL statements for schema operations. The file also includes a `quote_value` method that prepares values for use in PostgreSQL queries, ensuring proper escaping and encoding. ### Docstring:

```python
"""
import psycopg2

from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.backends.ddl_references import IndexColumns
from django.db.backends.utils import strip_quotes


class DatabaseSchemaEditor(BaseDatabaseSchemaEditor):

    sql_create_sequence = "CREATE SEQUENCE %(sequence)s"
    sql_delete_sequence = "DROP SEQUENCE IF EXISTS %(sequence)s CASCADE"
    sql_set_sequence_max = "SELECT setval('%(sequence)s', MAX(%(column)s)) FROM %(table)s"
    sql_set_sequence_owner = 'ALTER SEQUENCE %(sequence)s OWNED BY %(table)s.%(column)s'

    sql_create_index = (
        'CREATE INDEX %(name)s ON %(table)s%(using)s '
        '(%(columns)s)%(include)s%(extra)s%(condition)s'
    )
    sql_create_index_concurrently = (
        'CREATE INDEX CONCURRENTLY %(name)s ON %(table)s%(using)s '
        '(%(columns)s)%(include)s%(extra)s%(condition)s'
    )
    sql_delete_index = "DROP INDEX IF EXISTS %(name)s"
    sql_delete_index_concurrently = "DROP INDEX CONCURRENTLY IF EXISTS %(name)s"

    # Setting the constraint to IMMEDIATE to allow changing data in the same
    # transaction.
    sql_create_column_inline_fk = (
        'CONSTRAINT %(name)s REFERENCES %(to_table)s(%(to_column)s)%(deferrable)s'
        '; SET CONSTRAINTS %(namespace)s%(name)s IMMEDIATE'
    )
    # Setting the constraint to IMMEDIATE runs any deferred checks to allow
    # dropping it in the same transaction.
    sql_delete_fk = "SET CONSTRAINTS %(name)s IMMEDIATE; ALTER TABLE %(table)s DROP CONSTRAINT %(name)s"

    sql_delete_procedure = 'DROP FUNCTION %(procedure)s(%(param_types)s)'

    def quote_value(self, value):
        """
        Quote and adapt a given value for use with PostgreSQL.
        
        This function takes an input value and performs the following operations:
        - Replaces '%' characters with '%%' if the value is a string.
        - Adapts the value using `psycopg2.extensions.adapt`.
        - Sets the encoding of the adapted value to 'utf8'.
        - Returns the quoted and encoded representation of the adapted value.
        
        Args:
        value (str or any): The input value to be quoted
        """

        if isinstance(value, str):
            value = value.replace('%', '%%')
        adapted = psycopg2.extensions.adapt(value)
        if hasattr(adapted, 'encoding'):
            adapted.encoding = 'utf8'
        # getquoted() returns a quoted bytestring of the adapted value.
        return adapted.getquoted().decode()

    def _field_indexes_sql(self, model, field):
        """
        Generates SQL statements for field indexes and optionally appends a LIKE index statement.
        
        Args:
        model: The Django model class for which the indexes are being generated.
        field: The Django model field for which the indexes are being generated.
        
        Returns:
        A list of SQL statements representing the field indexes, potentially including a LIKE index statement.
        
        This method first calls the superclass's `_field_indexes_sql` method to generate the initial set of index SQL statements. It then checks if a LIKE
        """

        output = super()._field_indexes_sql(model, field)
        like_index_statement = self._create_like_index_sql(model, field)
        if like_index_statement is not None:
            output.append(like_index_statement)
        return output

    def _field_data_type(self, field):
        """
        Retrieve the database data type for a given field.
        
        Args:
        field (Field): The field object for which to determine the database data type.
        
        Returns:
        str: The database data type corresponding to the field.
        
        Summary:
        This function determines the database data type for a given field. If the field is a relation, it uses the `rel_db_type` method of the connection object. Otherwise, it retrieves the data type from the connection's `data_types` dictionary using the
        """

        if field.is_relation:
            return field.rel_db_type(self.connection)
        return self.connection.data_types.get(
            field.get_internal_type(),
            field.db_type(self.connection),
        )

    def _field_base_data_types(self, field):
        """
        Generates base data types for array fields.
        
        Args:
        field (Field): The field object to process.
        
        Yields:
        str: Base data type of the field or its base field.
        
        This function recursively processes array fields by yielding their base data types. If the field is an array field, it yields the base field's data type by recursively calling itself on the base field. Otherwise, it yields the data type of the current field.
        """

        # Yield base data types for array fields.
        if field.base_field.get_internal_type() == 'ArrayField':
            yield from self._field_base_data_types(field.base_field)
        else:
            yield self._field_data_type(field.base_field)

    def _create_like_index_sql(self, model, field):
        """
        Return the statement to create an index with varchar operator pattern
        when the column type is 'varchar' or 'text', otherwise return None.
        """
        db_type = field.db_type(connection=self.connection)
        if db_type is not None and (field.db_index or field.unique):
            # Fields with database column types of `varchar` and `text` need
            # a second index that specifies their operator class, which is
            # needed when performing correct LIKE queries outside the
            # C locale. See #12234.
            #
            # The same doesn't apply to array fields such as varchar[size]
            # and text[size], so skip them.
            if '[' in db_type:
                return None
            if db_type.startswith('varchar'):
                return self._create_index_sql(
                    model,
                    fields=[field],
                    suffix='_like',
                    opclasses=['varchar_pattern_ops'],
                )
            elif db_type.startswith('text'):
                return self._create_index_sql(
                    model,
                    fields=[field],
                    suffix='_like',
                    opclasses=['text_pattern_ops'],
                )
        return None

    def _alter_column_type_sql(self, model, old_field, new_field, new_type):
        """
        This function alters the data type of a column in a database table.
        
        Args:
        model: The Django model class representing the table.
        old_field: The old field object representing the column before the alteration.
        new_field: The new field object representing the column after the alteration.
        new_type: The new data type for the column.
        
        Returns:
        A tuple containing two elements:
        1. A SQL query string for altering the column type.
        2. A list
        """

        self.sql_alter_column_type = 'ALTER COLUMN %(column)s TYPE %(type)s'
        # Cast when data type changed.
        using_sql = ' USING %(column)s::%(type)s'
        new_internal_type = new_field.get_internal_type()
        old_internal_type = old_field.get_internal_type()
        if new_internal_type == 'ArrayField' and new_internal_type == old_internal_type:
            # Compare base data types for array fields.
            if list(self._field_base_data_types(old_field)) != list(self._field_base_data_types(new_field)):
                self.sql_alter_column_type += using_sql
        elif self._field_data_type(old_field) != self._field_data_type(new_field):
            self.sql_alter_column_type += using_sql
        # Make ALTER TYPE with SERIAL make sense.
        table = strip_quotes(model._meta.db_table)
        serial_fields_map = {'bigserial': 'bigint', 'serial': 'integer', 'smallserial': 'smallint'}
        if new_type.lower() in serial_fields_map:
            column = strip_quotes(new_field.column)
            sequence_name = "%s_%s_seq" % (table, column)
            return (
                (
                    self.sql_alter_column_type % {
                        "column": self.quote_name(column),
                        "type": serial_fields_map[new_type.lower()],
                    },
                    [],
                ),
                [
                    (
                        self.sql_delete_sequence % {
                            "sequence": self.quote_name(sequence_name),
                        },
                        [],
                    ),
                    (
                        self.sql_create_sequence % {
                            "sequence": self.quote_name(sequence_name),
                        },
                        [],
                    ),
                    (
                        self.sql_alter_column % {
                            "table": self.quote_name(table),
                            "changes": self.sql_alter_column_default % {
                                "column": self.quote_name(column),
                                "default": "nextval('%s')" % self.quote_name(sequence_name),
                            }
                        },
                        [],
                    ),
                    (
                        self.sql_set_sequence_max % {
                            "table": self.quote_name(table),
                            "column": self.quote_name(column),
                            "sequence": self.quote_name(sequence_name),
                        },
                        [],
                    ),
                    (
                        self.sql_set_sequence_owner % {
                            'table': self.quote_name(table),
                            'column': self.quote_name(column),
                            'sequence': self.quote_name(sequence_name),
                        },
                        [],
                    ),
                ],
            )
        elif old_field.db_parameters(connection=self.connection)['type'] in serial_fields_map:
            # Drop the sequence if migrating away from AutoField.
            column = strip_quotes(new_field.column)
            sequence_name = '%s_%s_seq' % (table, column)
            fragment, _ = super()._alter_column_type_sql(model, old_field, new_field, new_type)
            return fragment, [
                (
                    self.sql_delete_sequence % {
                        'sequence': self.quote_name(sequence_name),
                    },
                    [],
                ),
            ]
        else:
            return super()._alter_column_type_sql(model, old_field, new_field, new_type)

    def _alter_field(self, model, old_field, new_field, old_type, new_type,
        """
        _alter_field method alters a field in a Django model. It drops indexes on varchar/text/citext columns that are changing to a different type, and creates or removes PostgreSQL-specific indexes based on the changes in the field's properties.
        
        Args:
        model: The Django model instance being altered.
        old_field: The original field being replaced.
        new_field: The new field replacing the old one.
        old_type: The data type of the old field.
        new_type: The data
        """

                     old_db_params, new_db_params, strict=False):
        # Drop indexes on varchar/text/citext columns that are changing to a
        # different type.
        if (old_field.db_index or old_field.unique) and (
            (old_type.startswith('varchar') and not new_type.startswith('varchar')) or
            (old_type.startswith('text') and not new_type.startswith('text')) or
            (old_type.startswith('citext') and not new_type.startswith('citext'))
        ):
            index_name = self._create_index_name(model._meta.db_table, [old_field.column], suffix='_like')
            self.execute(self._delete_index_sql(model, index_name))

        super()._alter_field(
            model, old_field, new_field, old_type, new_type, old_db_params,
            new_db_params, strict,
        )
        # Added an index? Create any PostgreSQL-specific indexes.
        if ((not (old_field.db_index or old_field.unique) and new_field.db_index) or
                (not old_field.unique and new_field.unique)):
            like_index_statement = self._create_like_index_sql(model, new_field)
            if like_index_statement is not None:
                self.execute(like_index_statement)

        # Removed an index? Drop any PostgreSQL-specific indexes.
        if old_field.unique and not (new_field.db_index or new_field.unique):
            index_to_remove = self._create_index_name(model._meta.db_table, [old_field.column], suffix='_like')
            self.execute(self._delete_index_sql(model, index_to_remove))

    def _index_columns(self, table, columns, col_suffixes, opclasses):
        if opclasses:
            return IndexColumns(table, columns, self.quote_name, col_suffixes=col_suffixes, opclasses=opclasses)
        return super()._index_columns(table, columns, col_suffixes, opclasses)

    def add_index(self, model, index, concurrently=False):
        self.execute(index.create_sql(model, self, concurrently=concurrently), params=None)

    def remove_index(self, model, index, concurrently=False):
        self.execute(index.remove_sql(model, self, concurrently=concurrently))

    def _delete_index_sql(self, model, name, sql=None, concurrently=False):
        sql = self.sql_delete_index_concurrently if concurrently else self.sql_delete_index
        return super()._delete_index_sql(model, name, sql)

    def _create_index_sql(
        self, model, *, fields=None, name=None, suffix='', using='',
        db_tablespace=None, col_suffixes=(), sql=None, opclasses=(),
        condition=None, concurrently=False, include=None, expressions=None,
    ):
        sql = self.sql_create_index if not concurrently else self.sql_create_index_concurrently
        return super()._create_index_sql(
            model, fields=fields, name=name, suffix=suffix, using=using,
            db_tablespace=db_tablespace, col_suffixes=col_suffixes, sql=sql,
            opclasses=opclasses, condition=condition, include=include,
            expressions=expressions,
        )
