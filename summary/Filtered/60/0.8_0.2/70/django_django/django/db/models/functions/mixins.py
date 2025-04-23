import sys

from django.db.models.fields import DecimalField, FloatField, IntegerField
from django.db.models.functions import Cast


class FixDecimalInputMixin:

    def as_postgresql(self, compiler, connection, **extra_context):
        """
        Generates a PostgreSQL-specific SQL query for a given expression.
        
        This function is designed to handle the conversion of floating-point fields to decimal fields for PostgreSQL, which does not support certain floating-point operations directly. It casts the floating-point fields to decimal fields and then generates the SQL query.
        
        Parameters:
        compiler (Compiler): The compiler object used to generate SQL.
        connection (Connection): The database connection object.
        extra_context (dict): Additional context for the query generation.
        
        Returns:
        Query: A
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
        sql, params = super().as_sql(compiler, connection, **extra_context)
        if self.output_field.get_internal_type() == 'DurationField':
            sql = 'CAST(%s AS SIGNED)' % sql
        return sql, params

    def as_oracle(self, compiler, connection, **extra_context):
        """
        Generate a SQL representation for the duration field in Oracle database.
        
        This method is used to convert a duration field into a SQL expression that is compatible with Oracle's database backend. It handles the conversion of duration fields to and from seconds, which is necessary for proper representation in SQL queries.
        
        Parameters:
        compiler (SQLCompiler): The SQL compiler instance used to compile the SQL query.
        connection (Connection): The database connection object.
        extra_context (dict): Additional context for the SQL compilation process.
        
        Returns
        """

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
