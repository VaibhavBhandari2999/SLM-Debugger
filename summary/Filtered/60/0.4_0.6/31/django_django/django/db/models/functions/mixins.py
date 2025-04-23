import sys

from django.db.models.fields import DecimalField, FloatField, IntegerField
from django.db.models.functions import Cast


class FixDecimalInputMixin:

    def as_postgresql(self, compiler, connection, **extra_context):
        """
        Generates a PostgreSQL-specific SQL query for a given expression.
        
        This method is used to adapt a given expression for use in PostgreSQL, particularly for FloatField types which need to be cast to DecimalField to support certain PostgreSQL functions.
        
        Parameters:
        compiler (Compiler): The SQL compiler instance.
        connection (Connection): The database connection object.
        extra_context (dict): Additional context for the compilation process.
        
        Returns:
        Query: A modified query object with the necessary casts applied.
        
        Key Points:
        - The
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
        Generates a MySQL-specific SQL query for a given field.
        
        This function is designed to be used with Django's database query compiler. It takes a field and generates a MySQL-specific SQL query for it. If the field is a DurationField, it casts the field to a signed integer for proper handling.
        
        Parameters:
        compiler (Compiler): The database query compiler instance.
        connection (Connection): The database connection object.
        extra_context (dict): Additional context for the query generation.
        
        Returns:
        tuple
        """

        sql, params = super().as_sql(compiler, connection, **extra_context)
        if self.output_field.get_internal_type() == 'DurationField':
            sql = 'CAST(%s AS SIGNED)' % sql
        return sql, params

    def as_oracle(self, compiler, connection, **extra_context):
        if self.output_field.get_internal_type() == 'DurationField':
            expression = self.get_source_expressions()[0]
            options = self._get_repr_options()
            from django.db.backends.oracle.functions import IntervalToSeconds, SecondsToInterval
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
ut_field() if source_fields else FloatField()
