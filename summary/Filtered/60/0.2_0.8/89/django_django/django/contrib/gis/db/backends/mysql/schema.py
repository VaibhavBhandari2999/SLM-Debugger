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
        # Geometry fields are stored as BLOB/TEXT, for which MySQL < 8.0.13
        # doesn't support defaults.
        if isinstance(field, GeometryField) and not self._supports_limited_data_type_defaults:
            return True
        return super().skip_default(field)

    def quote_value(self, value):
        """
        Quote a value for use in a SQL query.
        
        This method is used to safely quote a value for inclusion in a SQL query to prevent SQL injection. It handles special cases where the value is an instance of `self.connection.ops.Adapter`, in which case it converts the value to a string before quoting. For all other types of values, it uses the superclass's `quote_value` method to perform the quoting.
        
        Parameters:
        value (Any): The value to be quoted for use in a SQL query
        """

        if isinstance(value, self.connection.ops.Adapter):
            return super().quote_value(str(value))
        return super().quote_value(value)

    def column_sql(self, model, field, include_default=False):
        """
        Generates SQL for a database column based on the given model and field.
        
        This function extends the behavior of the base class's `column_sql` method by adding spatial indexes for non-null geometry fields in MySQL databases. The function checks if the field is a `GeometryField`, if it has a spatial index, and if it is not nullable. If these conditions are met, it appends a SQL statement to create a spatial index to a list of geometry SQL statements.
        
        Parameters:
        model (Model
        """

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
        """
        Removes a field from a model, handling spatial indexes for GeometryFields.
        
        This method first checks if the field to be removed is a GeometryField with a spatial index. If it is, it attempts to drop the associated spatial index. If the operation fails due to an OperationalError, it logs an error message indicating that the spatial index removal may be expected if the storage engine does not support spatial indexes. After handling the spatial index, it calls the superclass's remove_field method to proceed with the field
        """

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
        for sql in self.geometry_sql:
            try:
                self.execute(sql)
            except OperationalError:
                logger.error(
                    "Cannot create SPATIAL INDEX %s. Only MyISAM and (as of "
                    "MySQL 5.7.5) InnoDB support them.", sql
                )
        self.geometry_sql = []
f.geometry_sql = []
