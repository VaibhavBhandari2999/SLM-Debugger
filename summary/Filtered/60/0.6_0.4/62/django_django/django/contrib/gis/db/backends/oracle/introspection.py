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
        Function to reverse the data types mapping for a database connection.
        
        This function is designed to reverse the data type mapping for a database connection, specifically for cx_Oracle. It extends the default behavior by adding a special mapping for the cx_Oracle.OBJECT data type to 'GeometryField'.
        
        Parameters:
        None
        
        Returns:
        dict: A dictionary where keys are data types and values are corresponding field types. The dictionary includes the default mappings and an additional mapping for cx_Oracle.OBJECT to 'Geometry
        """

        return {
            **super().data_types_reverse,
            cx_Oracle.OBJECT: 'GeometryField',
        }

    def get_geometry_type(self, table_name, description):
        """
        Retrieve the geometry type and parameters for a given table and column.
        
        This function queries the USER_SDO_GEOM_METADATA view to determine the geometry type and parameters for a specified table and column. It returns a tuple containing the geometry field type and a dictionary of field parameters.
        
        Parameters:
        table_name (str): The name of the table containing the geometry column.
        description (GeometryDescription): An object containing information about the geometry column.
        
        Returns:
        tuple: A tuple where the first element is the
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
