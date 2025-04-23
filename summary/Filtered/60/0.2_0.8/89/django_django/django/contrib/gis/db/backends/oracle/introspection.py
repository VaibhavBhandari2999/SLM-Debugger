import cx_Oracle

from django.db.backends.oracle.introspection import DatabaseIntrospection
from django.utils.functional import cached_property


class OracleIntrospection(DatabaseIntrospection):
    # Associating any OBJECTVAR instances with GeometryField. This won't work
    # right on Oracle objects that aren't MDSYS.SDO_GEOMETRY, but it is the
    # only object type supported within Django anyways.
    @cached_property
    def data_types_reverse(self):
        """
        Reverses the order of data type mappings for a database adapter.
        
        This function updates the data type mappings by reversing the order of the mappings from the superclass and adding a new mapping for cx_Oracle.OBJECT to 'GeometryField'.
        
        Parameters:
        None
        
        Returns:
        dict: A dictionary of data type mappings where the keys are database data types and the values are the corresponding Django field types.
        
        Example usage:
        >>> data_types_reverse()
        {<class 'django.db.backends.utils.CursorDebug
        """

        return {
            **super().data_types_reverse,
            cx_Oracle.OBJECT: 'GeometryField',
        }

    def get_geometry_type(self, table_name, description):
        """
        Retrieve the geometry type and parameters for a given table and column.
        
        This function queries the `USER_SDO_GEOM_METADATA` view to obtain the spatial
        metadata for a specified table and column. It returns the geometry field type
        and parameters such as SRID and dimensions.
        
        Parameters:
        table_name (str): The name of the table containing the spatial column.
        description (SpatialDescription): An object containing the column name
        and other spatial metadata.
        
        Returns:
        tuple: A tuple containing
        """

        with self.connection.cursor() as cursor:
            # Querying USER_SDO_GEOM_METADATA to get the SRID and dimension information.
            try:
                cursor.execute(
                    'SELECT "DIMINFO", "SRID" FROM "USER_SDO_GEOM_METADATA" '
                    'WHERE "TABLE_NAME"=%s AND "COLUMN_NAME"=%s',
                    (table_name.upper(), description.name.upper())
                )
                row = cursor.fetchone()
            except Exception as exc:
                raise Exception(
                    'Could not find entry in USER_SDO_GEOM_METADATA '
                    'corresponding to "%s"."%s"' % (table_name, description.name)
                ) from exc

            # TODO: Research way to find a more specific geometry field type for
            # the column's contents.
            field_type = 'GeometryField'

            # Getting the field parameters.
            field_params = {}
            dim, srid = row
            if srid != 4326:
                field_params['srid'] = srid
            # Size of object array (SDO_DIM_ARRAY) is number of dimensions.
            dim = dim.size()
            if dim != 2:
                field_params['dim'] = dim
        return field_type, field_params
