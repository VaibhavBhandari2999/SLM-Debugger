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
        Determines whether a field should skip the default value.
        
        This method checks if the given field should skip its default value based on its type and the database version. For fields of type `GeometryField`, it returns `True` if the database version is less than 8.0.13, as MySQL versions prior to 8.0.13 do not support default values for BLOB/TEXT fields. Otherwise, it delegates the decision to the superclass method `skip_default`.
        
        Parameters:
        """

        # Geometry fields are stored as BLOB/TEXT, for which MySQL < 8.0.13
        # doesn't support defaults.
        if isinstance(field, GeometryField) and not self._supports_limited_data_type_defaults:
            return True
        return super().skip_default(field)

    def quote_value(self, value):
        if isinstance(value, self.connection.ops.Adapter):
            return super().quote_value(str(value))
        return super().quote_value(value)

    def column_sql(self, model, field, include_default=False):
        """
        Generates the SQL for a database column based on the provided model and field.
        
        This function extends the behavior of the base class's `column_sql` method to handle specific requirements for MySQL databases, particularly for `GeometryField` types. It appends a spatial index to the SQL if the field is not nullable and a spatial index is required.
        
        Parameters:
        model (Model): The Django model class for which the column is being defined.
        field (Field): The Django field object for which the
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
        
        This method is an overridden version of the original `remove_field` method. It first checks if the field being removed is a GeometryField with a spatial index. If so, it drops the corresponding spatial index from the database. After handling spatial indexes, it calls the superclass's `remove_field` method to proceed with the field removal.
        
        Parameters:
        model (Model): The model from which the field is being removed.
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
