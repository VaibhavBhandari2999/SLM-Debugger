from django.contrib.gis.db.models.fields import (
    ExtentField, GeometryCollectionField, GeometryField, LineStringField,
)
from django.db.models import Aggregate, Value
from django.utils.functional import cached_property

__all__ = ['Collect', 'Extent', 'Extent3D', 'MakeLine', 'Union']


class GeoAggregate(Aggregate):
    function = None
    is_extent = False

    @cached_property
    def output_field(self):
        return self.output_field_class(self.source_expressions[0].output_field.srid)

    def as_sql(self, compiler, connection, function=None, **extra_context):
        """
        Generates a SQL query for a spatial aggregate function.
        
        This method is used to generate a SQL query for a spatial aggregate function. It first checks if the expression is supported by the database connection's operations. Then, it calls the superclass's `as_sql` method with the appropriate parameters, including the spatial aggregate function name, which is determined based on the name of the spatial field.
        
        Parameters:
        compiler (sql.compiler.SQLCompiler): The SQL compiler instance.
        connection (django.db.backends.base.Base
        """

        # this will be called again in parent, but it's needed now - before
        # we get the spatial_aggregate_name
        connection.ops.check_expression_support(self)
        return super().as_sql(
            compiler,
            connection,
            function=function or connection.ops.spatial_aggregate_name(self.name),
            **extra_context
        )

    def as_oracle(self, compiler, connection, **extra_context):
        """
        Generate an Oracle SQL query for a spatial aggregation operation.
        
        This method is used to create an Oracle SQL query for performing a spatial
        aggregation operation on a geometry field. It can be customized with a
        tolerance value for the aggregation.
        
        Parameters:
        compiler (sqlCompiler): The SQL compiler instance used to compile the query.
        connection (Connection): The database connection object.
        extra_context (dict): Additional context for the SQL template.
        
        Returns:
        str: The generated SQL query string
        """

        if not self.is_extent:
            tolerance = self.extra.get('tolerance') or getattr(self, 'tolerance', 0.05)
            clone = self.copy()
            clone.set_source_expressions([
                *self.get_source_expressions(),
                Value(tolerance),
            ])
            template = '%(function)s(SDOAGGRTYPE(%(expressions)s))'
            return clone.as_sql(compiler, connection, template=template, **extra_context)
        return self.as_sql(compiler, connection, **extra_context)

    def resolve_expression(self, query=None, allow_joins=True, reuse=None, summarize=False, for_save=False):
        c = super().resolve_expression(query, allow_joins, reuse, summarize, for_save)
        for expr in c.get_source_expressions():
            if not hasattr(expr.field, 'geom_type'):
                raise ValueError('Geospatial aggregates only allowed on geometry fields.')
        return c


class Collect(GeoAggregate):
    name = 'Collect'
    output_field_class = GeometryCollectionField


class Extent(GeoAggregate):
    name = 'Extent'
    is_extent = '2D'

    def __init__(self, expression, **extra):
        super().__init__(expression, output_field=ExtentField(), **extra)

    def convert_value(self, value, expression, connection):
        return connection.ops.convert_extent(value)


class Extent3D(GeoAggregate):
    name = 'Extent3D'
    is_extent = '3D'

    def __init__(self, expression, **extra):
        super().__init__(expression, output_field=ExtentField(), **extra)

    def convert_value(self, value, expression, connection):
        return connection.ops.convert_extent3d(value)


class MakeLine(GeoAggregate):
    name = 'MakeLine'
    output_field_class = LineStringField


class Union(GeoAggregate):
    name = 'Union'
    output_field_class = GeometryField
