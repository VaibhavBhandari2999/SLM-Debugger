import sys

from django.db.models.fields import DecimalField, FloatField, IntegerField
from django.db.models.functions import Cast


class FixDecimalInputMixin:

    def as_postgresql(self, compiler, connection, **extra_context):
        """
        Generates a PostgreSQL-specific SQL query for the given expression.
        
        This function is responsible for converting FloatField expressions to DecimalField expressions to ensure compatibility with PostgreSQL's SQL functions. It creates a clone of the current expression, casts any FloatField to DecimalField, and then returns the SQL representation of the modified expression.
        
        Parameters:
        - compiler: The SQL compiler instance used to generate the SQL query.
        - connection: The database connection object.
        - extra_context: Additional context for the SQL generation process.
        
        Returns:
        """

        # Cast FloatField to DecimalField as PostgreSQL doesn't support the
        # following function signatures:
        # - LOG(double, double)
        # - MOD(double, double)
        output_field = DecimalField(decimal_places=sys.float_info.dig, max_digits=1000)
        clone = self.copy()
        clone.set_source_expressions([
            Cast(expression, output_field) if isinstance(expression.output_field, FloatField)
            else expression for expression in self.get_source_expressions()
        ])
        return clone.as_sql(compiler, connection, **extra_context)


class FixDurationInputMixin:

    def as_mysql(self, compiler, connection, **extra_context):
        """
        Generates a SQL query for a MySQL database.
        
        This method is used to generate a SQL query for a MySQL database, specifically tailored for fields that are instances of `DurationField`. The generated SQL includes a type cast to ensure the duration field is treated as a signed integer.
        
        Parameters:
        compiler (Compiler): The compiler object used to generate the SQL query.
        connection (Connection): The database connection object.
        extra_context (dict): Additional context that may be required for generating the SQL query.
        """

        sql, params = super().as_sql(compiler, connection, **extra_context)
        if self.output_field.get_internal_type() == 'DurationField':
            sql = 'CAST(%s AS SIGNED)' % sql
        return sql, params

    def as_oracle(self, compiler, connection, **extra_context):
        if self.output_field.get_internal_type() == 'DurationField':
            expression = self.get_source_expressions()[0]
            options = self._get_repr_options()
            from django.db.backends.oracle.functions import (
                IntervalToSeconds, SecondsToInterval,
            )
            return compiler.compile(
                SecondsToInterval(self.__class__(IntervalToSeconds(expression), **options))
            )
        return super().as_sql(compiler, connection, **extra_context)


class NumericOutputFieldMixin:

    def _resolve_output_field(self):
        source_fields = self.get_source_fields()
        if any(isinstance(s, DecimalField) for s in source_fields):
            return DecimalField()
        if any(isinstance(s, IntegerField) for s in source_fields):
            return FloatField()
        return super()._resolve_output_field() if source_fields else FloatField()
