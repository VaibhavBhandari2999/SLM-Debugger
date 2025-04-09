from collections import defaultdict, namedtuple

from django.contrib.gis import forms, gdal
from django.contrib.gis.db.models.proxy import SpatialProxy
from django.contrib.gis.gdal.error import GDALException
from django.contrib.gis.geos import (
    GeometryCollection,
    GEOSException,
    GEOSGeometry,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Field
from django.utils.translation import gettext_lazy as _

# Local cache of the spatial_ref_sys table, which holds SRID data for each
# spatial database alias. This cache exists so that the database isn't queried
# for SRID info each time a distance query is constructed.
_srid_cache = defaultdict(dict)


SRIDCacheEntry = namedtuple(
    "SRIDCacheEntry", ["units", "units_name", "spheroid", "geodetic"]
)


def get_srid_info(srid, connection):
    """
    Return the units, unit name, and spheroid WKT associated with the
    given SRID from the `spatial_ref_sys` (or equivalent) spatial database
    table for the given database connection.  These results are cached.
    """
    from django.contrib.gis.gdal import SpatialReference

    global _srid_cache

    try:
        # The SpatialRefSys model for the spatial backend.
        SpatialRefSys = connection.ops.spatial_ref_sys()
    except NotImplementedError:
        SpatialRefSys = None

    alias, get_srs = (
        (
            connection.alias,
            lambda srid: SpatialRefSys.objects.using(connection.alias)
            .get(srid=srid)
            .srs,
        )
        if SpatialRefSys
        else (None, SpatialReference)
    )
    if srid not in _srid_cache[alias]:
        srs = get_srs(srid)
        units, units_name = srs.units
        _srid_cache[alias][srid] = SRIDCacheEntry(
            units=units,
            units_name=units_name,
            spheroid='SPHEROID["%s",%s,%s]'
            % (srs["spheroid"], srs.semi_major, srs.inverse_flattening),
            geodetic=srs.geographic,
        )

    return _srid_cache[alias][srid]


class BaseSpatialField(Field):
    """
    The Base GIS Field.

    It's used as a base class for GeometryField and RasterField. Defines
    properties that are common to all GIS fields such as the characteristics
    of the spatial reference system of the field.
    """

    description = _("The base GIS field.")
    empty_strings_allowed = False

    def __init__(self, verbose_name=None, srid=4326, spatial_index=True, **kwargs):
        """
        The initialization function for base spatial fields. Takes the following
        as keyword arguments:

        srid:
         The spatial reference system identifier, an OGC standard.
         Defaults to 4326 (WGS84).

        spatial_index:
         Indicates whether to create a spatial index.  Defaults to True.
         Set this instead of 'db_index' for geographic fields since index
         creation is different for geometry columns.
        """

        # Setting the index flag with the value of the `spatial_index` keyword.
        self.spatial_index = spatial_index

        # Setting the SRID and getting the units.  Unit information must be
        # easily available in the field instance for distance queries.
        self.srid = srid

        # Setting the verbose_name keyword argument with the positional
        # first parameter, so this works like normal fields.
        kwargs["verbose_name"] = verbose_name

        super().__init__(**kwargs)

    def deconstruct(self):
        """
        Deconstructs the current instance into its constituent parts.
        
        This method is used to break down the instance into its key components,
        including the name, path, arguments, and keyword arguments. It ensures that
        the SRID (Spatial Reference System Identifier) is always included for
        consistency. Additionally, it includes the spatial index setting unless it
        is set to the default value.
        
        Args:
        None
        
        Returns:
        tuple: A tuple containing the name, path,
        """

        name, path, args, kwargs = super().deconstruct()
        # Always include SRID for less fragility; include spatial index if it's
        # not the default value.
        kwargs["srid"] = self.srid
        if self.spatial_index is not True:
            kwargs["spatial_index"] = self.spatial_index
        return name, path, args, kwargs

    def db_type(self, connection):
        return connection.ops.geo_db_type(self)

    def spheroid(self, connection):
        return get_srid_info(self.srid, connection).spheroid

    def units(self, connection):
        return get_srid_info(self.srid, connection).units

    def units_name(self, connection):
        return get_srid_info(self.srid, connection).units_name

    def geodetic(self, connection):
        """
        Return true if this field's SRID corresponds with a coordinate
        system that uses non-projected units (e.g., latitude/longitude).
        """
        return get_srid_info(self.srid, connection).geodetic

    def get_placeholder(self, value, compiler, connection):
        """
        Return the placeholder for the spatial column for the
        given value.
        """
        return connection.ops.get_geom_placeholder(self, value, compiler)

    def get_srid(self, obj):
        """
        Return the default SRID for the given geometry or raster, taking into
        account the SRID set for the field. For example, if the input geometry
        or raster doesn't have an SRID, then the SRID of the field will be
        returned.
        """
        srid = obj.srid  # SRID of given geometry.
        if srid is None or self.srid == -1 or (srid == -1 and self.srid != -1):
            return self.srid
        else:
            return srid

    def get_db_prep_value(self, value, connection, *args, **kwargs):
        """
        Generates a database-prepared value for a geography field.
        
        This function prepares a value for storage in a database by applying
        necessary transformations and ensuring compatibility with the database's
        geography support features. It handles cases where the input value is `None`
        and applies specific adaptations based on the `geography` attribute and the
        database's capabilities.
        
        Args:
        value (Any): The value to be prepared for database storage.
        connection (Connection): The database connection object
        """

        if value is None:
            return None
        return connection.ops.Adapter(
            super().get_db_prep_value(value, connection, *args, **kwargs),
            **(
                {"geography": True}
                if self.geography and connection.features.supports_geography
                else {}
            ),
        )

    def get_raster_prep_value(self, value, is_candidate):
        """
        Return a GDALRaster if conversion is successful, otherwise return None.
        """
        if isinstance(value, gdal.GDALRaster):
            return value
        elif is_candidate:
            try:
                return gdal.GDALRaster(value)
            except GDALException:
                pass
        elif isinstance(value, dict):
            try:
                return gdal.GDALRaster(value)
            except GDALException:
                raise ValueError(
                    "Couldn't create spatial object from lookup value '%s'." % value
                )

    def get_prep_value(self, value):
        """
        Converts the input value to a suitable format for database storage.
        
        This method takes an input value, attempts to convert it into a `GEOSGeometry` or `raster` object,
        and assigns a Spatial Reference System ID (SRID) to the resulting object. If the input cannot be
        converted into a valid spatial object, a `ValueError` is raised.
        
        Args:
        value: The input value to be converted.
        
        Returns:
        A `GEOSGeometry
        """

        obj = super().get_prep_value(value)
        if obj is None:
            return None
        # When the input is not a geometry or raster, attempt to construct one
        # from the given string input.
        if isinstance(obj, GEOSGeometry):
            pass
        else:
            # Check if input is a candidate for conversion to raster or geometry.
            is_candidate = isinstance(obj, (bytes, str)) or hasattr(
                obj, "__geo_interface__"
            )
            # Try to convert the input to raster.
            raster = self.get_raster_prep_value(obj, is_candidate)

            if raster:
                obj = raster
            elif is_candidate:
                try:
                    obj = GEOSGeometry(obj)
                except (GEOSException, GDALException):
                    raise ValueError(
                        "Couldn't create spatial object from lookup value '%s'." % obj
                    )
            else:
                raise ValueError(
                    "Cannot use object with type %s for a spatial lookup parameter."
                    % type(obj).__name__
                )

        # Assigning the SRID value.
        obj.srid = self.get_srid(obj)
        return obj


class GeometryField(BaseSpatialField):
    """
    The base Geometry field -- maps to the OpenGIS Specification Geometry type.
    """

    description = _(
        "The base Geometry field — maps to the OpenGIS Specification Geometry type."
    )
    form_class = forms.GeometryField
    # The OpenGIS Geometry name.
    geom_type = "GEOMETRY"
    geom_class = None

    def __init__(
        self,
        verbose_name=None,
        dim=2,
        geography=False,
        *,
        extent=(-180.0, -90.0, 180.0, 90.0),
        tolerance=0.05,
        **kwargs,
    ):
        """
        The initialization function for geometry fields. In addition to the
        parameters from BaseSpatialField, it takes the following as keyword
        arguments:

        dim:
         The number of dimensions for this geometry.  Defaults to 2.

        extent:
         Customize the extent, in a 4-tuple of WGS 84 coordinates, for the
         geometry field entry in the `USER_SDO_GEOM_METADATA` table.  Defaults
         to (-180.0, -90.0, 180.0, 90.0).

        tolerance:
         Define the tolerance, in meters, to use for the geometry field
         entry in the `USER_SDO_GEOM_METADATA` table.  Defaults to 0.05.
        """
        # Setting the dimension of the geometry field.
        self.dim = dim

        # Is this a geography rather than a geometry column?
        self.geography = geography

        # Oracle-specific private attributes for creating the entry in
        # `USER_SDO_GEOM_METADATA`
        self._extent = extent
        self._tolerance = tolerance

        super().__init__(verbose_name=verbose_name, **kwargs)

    def deconstruct(self):
        """
        Deconstructs the object into its constituent parts.
        
        This method is used to break down the object into its fundamental components, allowing for serialization or other forms of data representation. The deconstruction process involves extracting the following attributes:
        
        - `name`: The name of the object.
        - `path`: The path to the object's class.
        - `args`: Positional arguments that were passed to the object during initialization.
        - `kwargs`: Keyword arguments that were passed to the object during
        """

        name, path, args, kwargs = super().deconstruct()
        # Include kwargs if they're not the default values.
        if self.dim != 2:
            kwargs["dim"] = self.dim
        if self.geography is not False:
            kwargs["geography"] = self.geography
        if self._extent != (-180.0, -90.0, 180.0, 90.0):
            kwargs["extent"] = self._extent
        if self._tolerance != 0.05:
            kwargs["tolerance"] = self._tolerance
        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, **kwargs):
        """
        Contributes to the class by setting up a lazy-instantiated Geometry object.
        
        Args:
        cls (class): The class to which the field is being contributed.
        name (str): The name of the attribute in the class.
        geom_class (type, optional): The geometry class to use for the lazy-instantiated object. Defaults to GEOSGeometry.
        load_func (callable, optional): The function to use for loading the lazy-instantiated object. Defaults to GEOS
        """

        super().contribute_to_class(cls, name, **kwargs)

        # Setup for lazy-instantiated Geometry object.
        setattr(
            cls,
            self.attname,
            SpatialProxy(self.geom_class or GEOSGeometry, self, load_func=GEOSGeometry),
        )

    def formfield(self, **kwargs):
        """
        Generates a form field for a geographic model field.
        
        This method configures and returns a form field for a geographic model field.
        It takes into account the `form_class`, `geom_type`, and `srid` attributes of the field.
        If the dimension of the geometry is greater than 2 and the form widget does not support 3D, it uses a Textarea widget instead.
        
        Args:
        **kwargs: Additional keyword arguments to be passed to the form field configuration
        """

        defaults = {
            "form_class": self.form_class,
            "geom_type": self.geom_type,
            "srid": self.srid,
            **kwargs,
        }
        if self.dim > 2 and not getattr(
            defaults["form_class"].widget, "supports_3d", False
        ):
            defaults.setdefault("widget", forms.Textarea)
        return super().formfield(**defaults)

    def select_format(self, compiler, sql, params):
        """
        Return the selection format string, depending on the requirements
        of the spatial backend. For example, Oracle and MySQL require custom
        selection formats in order to retrieve geometries in OGC WKB.
        """
        if not compiler.query.subquery:
            return compiler.connection.ops.select % sql, params
        return sql, params


# The OpenGIS Geometry Type Fields
class PointField(GeometryField):
    geom_type = "POINT"
    geom_class = Point
    form_class = forms.PointField
    description = _("Point")


class LineStringField(GeometryField):
    geom_type = "LINESTRING"
    geom_class = LineString
    form_class = forms.LineStringField
    description = _("Line string")


class PolygonField(GeometryField):
    geom_type = "POLYGON"
    geom_class = Polygon
    form_class = forms.PolygonField
    description = _("Polygon")


class MultiPointField(GeometryField):
    geom_type = "MULTIPOINT"
    geom_class = MultiPoint
    form_class = forms.MultiPointField
    description = _("Multi-point")


class MultiLineStringField(GeometryField):
    geom_type = "MULTILINESTRING"
    geom_class = MultiLineString
    form_class = forms.MultiLineStringField
    description = _("Multi-line string")


class MultiPolygonField(GeometryField):
    geom_type = "MULTIPOLYGON"
    geom_class = MultiPolygon
    form_class = forms.MultiPolygonField
    description = _("Multi polygon")


class GeometryCollectionField(GeometryField):
    geom_type = "GEOMETRYCOLLECTION"
    geom_class = GeometryCollection
    form_class = forms.GeometryCollectionField
    description = _("Geometry collection")


class ExtentField(Field):
    "Used as a return value from an extent aggregate"

    description = _("Extent Aggregate Field")

    def get_internal_type(self):
        return "ExtentField"

    def select_format(self, compiler, sql, params):
        select = compiler.connection.ops.select_extent
        return select % sql if select else sql, params


class RasterField(BaseSpatialField):
    """
    Raster field for GeoDjango -- evaluates into GDALRaster objects.
    """

    description = _("Raster Field")
    geom_type = "RASTER"
    geography = False

    def _check_connection(self, connection):
        """
        Checks if the given connection supports raster fields.
        
        Args:
        connection (DatabaseConnection): The database connection to check.
        
        Raises:
        ImproperlyConfigured: If the connection does not support raster fields.
        """

        # Make sure raster fields are used only on backends with raster support.
        if (
            not connection.features.gis_enabled
            or not connection.features.supports_raster
        ):
            raise ImproperlyConfigured(
                "Raster fields require backends with raster support."
            )

    def db_type(self, connection):
        self._check_connection(connection)
        return super().db_type(connection)

    def from_db_value(self, value, expression, connection):
        return connection.ops.parse_raster(value)

    def contribute_to_class(self, cls, name, **kwargs):
        """
        Contributes to the class by setting up a lazy-instantiated Raster object. This method is called during the model field setup process. It instantiates a `SpatialProxy` object that wraps a `GDALRaster` object, allowing for deferred instantiation of the raster data. This is particularly useful for large querysets where instantiating all rasters upfront would be computationally expensive.
        
        Args:
        cls (type): The Django model class to which this field is being added.
        name (
        """

        super().contribute_to_class(cls, name, **kwargs)
        # Setup for lazy-instantiated Raster object. For large querysets, the
        # instantiation of all GDALRasters can potentially be expensive. This
        # delays the instantiation of the objects to the moment of evaluation
        # of the raster attribute.
        setattr(cls, self.attname, SpatialProxy(gdal.GDALRaster, self))

    def get_transform(self, name):
        """
        Retrieve a specific raster band transformation.
        
        Args:
        name (str): The name or index of the raster band.
        
        Returns:
        SpecificRasterBandTransform: A custom transformation object for the specified raster band.
        
        Raises:
        ValueError: If the provided `name` is not an integer.
        
        Notes:
        - Utilizes :class:`django.contrib.gis.db.models.lookups.RasterBandTransform` to create the transformation.
        - If `name` is an integer,
        """

        from django.contrib.gis.db.models.lookups import RasterBandTransform

        try:
            band_index = int(name)
            return type(
                "SpecificRasterBandTransform",
                (RasterBandTransform,),
                {"band_index": band_index},
            )
        except ValueError:
            pass
        return super().get_transform(name)
