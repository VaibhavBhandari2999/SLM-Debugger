import logging

from django.contrib.gis.db.models import GeometryField
from django.db import OperationalError
from django.db.backends.mysql.schema import DatabaseSchemaEditor

logger = logging.getLogger('django.contrib.gis')


class MySQLGISSchemaEditor(DatabaseSchemaEditor):
    sql_add_spatial_index = 'CREATE SPATIAL INDEX %(index)s ON %(table)s(%(column)s)'
    sql_drop_spatial_index = 'DROP INDEX %(index)s ON %(table)s'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry_sql = []

    def skip_default(self, field):
        """
        Determines whether a default value should be skipped for a given field.
        
        This method checks if the provided field is a GeometryField and if the database version supports limited data type defaults. If the field is a GeometryField and the database version is less than 8.0.13, it returns True, indicating that the default value should be skipped. Otherwise, it calls the `skip_default` method from the superclass.
        
        Parameters:
        field (Field): The field for which to determine if the
        """

        # Geometry fields are stored as BLOB/TEXT, for which MySQL < 8.0.13
        # doesn't support defaults.
        if isinstance(field, GeometryField) and not self._supports_limited_data_type_defaults:
            return True
        return super().skip_default(field)

    def quote_value(self, value):
        """
        Quotes a value for use in a database query.
        
        This method is used to safely quote a value before it is inserted into a database query. It checks if the value is an instance of the `Adapter` class from the connection operations. If so, it converts the value to a string and quotes it using the parent class's `quote_value` method. Otherwise, it directly quotes the value using the parent class's `quote_value` method.
        
        Parameters:
        value (Any): The value to be
        """

        if isinstance(value, self.connection.ops.Adapter):
            return super().quote_value(str(value))
        return super().quote_value(value)

    def column_sql(self, model, field, include_default=False):
        column_sql = super().column_sql(model, field, include_default)
        # MySQL doesn't support spatial indexes on NULL columns
        if isinstance(field, GeometryField) and field.spatial_index and not field.null:
            qn = self.connection.ops.quote_name
            db_table = model._meta.db_table
            self.geometry_sql.append(
                self.sql_add_spatial_index % {
                    'index': qn(self._create_spatial_index_name(model, field)),
                    'table': qn(db_table),
                    'column': qn(field.column),
                }
            )
        return column_sql

    def create_model(self, model):
        super().create_model(model)
        self.create_spatial_indexes()

    def add_field(self, model, field):
        super().add_field(model, field)
        self.create_spatial_indexes()

    def remove_field(self, model, field):
        if isinstance(field, GeometryField) and field.spatial_index:
            qn = self.connection.ops.quote_name
            sql = self.sql_drop_spatial_index % {
                'index': qn(self._create_spatial_index_name(model, field)),
                'table': qn(model._meta.db_table),
            }
            try:
                self.execute(sql)
            except OperationalError:
                logger.error(
                    "Couldn't remove spatial index: %s (may be expected "
                    "if your storage engine doesn't support them).", sql
                )

        super().remove_field(model, field)

    def _create_spatial_index_name(self, model, field):
        return '%s_%s_id' % (model._meta.db_table, field.column)

    def create_spatial_indexes(self):
        """
        Creates spatial indexes for the specified geometries.
        
        This function iterates over a list of SQL statements that define spatial indexes for geometries. It attempts to execute each SQL statement. If an `OperationalError` is raised during the execution, it logs an error message indicating that only MyISAM and InnoDB storage engines support spatial indexes, and that the problematic SQL statement could not be executed. After attempting to create the indexes, it clears the list of SQL statements.
        
        Parameters:
        None
        
        Returns
        """

        for sql in self.geometry_sql:
            try:
                self.execute(sql)
            except OperationalError:
                logger.error(
                    "Cannot create SPATIAL INDEX %s. Only MyISAM and (as of "
                    "MySQL 5.7.5) InnoDB support them.", sql
                )
        self.geometry_sql = []
