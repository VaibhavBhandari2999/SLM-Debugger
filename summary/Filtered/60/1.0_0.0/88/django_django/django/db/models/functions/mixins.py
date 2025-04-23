import sys

from django.db.models.fields import DecimalField, FloatField, IntegerField
from django.db.models.functions import Cast


class FixDecimalInputMixin:

    def as_postgresql(self, compiler, connection, **extra_context):
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
        Generate a MySQL-specific SQL query for a given field.
        
        This method is used to generate a SQL query that is compatible with MySQL for a specific field. It first calls the superclass's as_sql method to get the initial SQL and parameters. If the field is a DurationField, it casts the SQL result to a signed integer using MySQL's CAST function. The method returns the modified SQL query and parameters.
        
        Parameters:
        compiler (sql.compiler.SQLCompiler): The SQL compiler instance used to compile the query.
        """

        sql, params = super().as_sql(compiler, connection, **extra_context)
        if self.output_field.get_internal_type() == 'DurationField':
            sql = 'CAST(%s AS SIGNED)' % sql
        return sql, params

    def as_oracle(self, compiler, connection, **extra_context):
        """
        Generate Oracle-specific SQL for the given expression.
        
        This method is used to generate the SQL representation of the expression for Oracle databases. It handles the special case where the output field is a 'DurationField'. In such cases, it converts the interval to seconds and then back to a duration format using the SecondsToInterval and IntervalToSeconds functions from the django.db.backends.oracle.functions module.
        
        Parameters:
        compiler (SQLCompiler): The SQL compiler instance used to compile the expression.
        connection (Connection): The
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
