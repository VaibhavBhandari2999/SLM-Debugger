"""
This Python file contains Django form widgets for handling geographic data. It defines three main classes:

1. **BaseGeometryWidget**: A base class for geometry widgets that provides common functionality for rendering and serializing geometry objects. It includes methods for initializing attributes, serializing and deserializing geometry objects, and generating context for form fields.

2. **OpenLayersWidget**: A subclass of `BaseGeometryWidget` that uses the OpenLayers library for rendering maps. It overrides the `serialize` and `deserialize` methods to handle GeoJSON formats and sets specific attributes for the OpenLayers widget.

3. **OSMWidget**: A subclass of `OpenLayersWidget` that specifically uses OpenStreetMap as the base map layer. It extends the functionality of `
"""
import logging

from django.conf import settings
from django.contrib.gis import gdal
from django.contrib.gis.geometry import json_regex
from django.contrib.gis.geos import GEOSException, GEOSGeometry
from django.forms.widgets import Widget
from django.utils import translation

logger = logging.getLogger('django.contrib.gis')


class BaseGeometryWidget(Widget):
    """
    The base class for rich geometry widgets.
    Render a map using the WKT of the geometry.
    """
    geom_type = 'GEOMETRY'
    map_srid = 4326
    map_width = 600
    map_height = 400
    display_raw = False

    supports_3d = False
    template_name = ''  # set on subclasses

    def __init__(self, attrs=None):
        """
        Initialize a GeoLayer object with optional attributes.
        
        Args:
        attrs (dict, optional): Additional attributes to set on the GeoLayer object.
        
        Attributes:
        attrs (dict): A dictionary containing various attributes of the GeoLayer object, including geom_type, map_srid, map_width, map_height, and display_raw. If `attrs` is provided, its contents are merged into the `attrs` dictionary.
        
        This method initializes a GeoLayer object by setting default values for certain attributes and
        """

        self.attrs = {}
        for key in ('geom_type', 'map_srid', 'map_width', 'map_height', 'display_raw'):
            self.attrs[key] = getattr(self, key)
        if attrs:
            self.attrs.update(attrs)

    def serialize(self, value):
        return value.wkt if value else ''

    def deserialize(self, value):
        """
        Deserialize a value into a GEOSGeometry object.
        
        Args:
        value (str): The value to be deserialized.
        
        Returns:
        GEOSGeometry: The deserialized GEOSGeometry object or None if an error occurs.
        
        Raises:
        GEOSException: If there is an error during deserialization.
        ValueError: If the input value is invalid.
        TypeError: If the input value is of an unexpected type.
        
        Notes:
        - This function attempts to create a GEOS
        """

        try:
            return GEOSGeometry(value)
        except (GEOSException, ValueError, TypeError) as err:
            logger.error("Error creating geometry from value '%s' (%s)", value, err)
        return None

    def get_context(self, name, value, attrs):
        """
        Generates a context dictionary for rendering a GeoDjango form field.
        
        Args:
        name (str): The name of the form field.
        value (str or Geometry): The value of the form field, either a serialized geometry string or a Geometry object.
        attrs (dict): Additional attributes for the form field.
        
        Returns:
        dict: A context dictionary containing the necessary information for rendering the form field.
        
        Summary:
        This function processes the form field's name, value, and
        """

        context = super().get_context(name, value, attrs)
        # If a string reaches here (via a validation error on another
        # field) then just reconstruct the Geometry.
        if value and isinstance(value, str):
            value = self.deserialize(value)

        if value:
            # Check that srid of value and map match
            if value.srid and value.srid != self.map_srid:
                try:
                    ogr = value.ogr
                    ogr.transform(self.map_srid)
                    value = ogr
                except gdal.GDALException as err:
                    logger.error(
                        "Error transforming geometry from srid '%s' to srid '%s' (%s)",
                        value.srid, self.map_srid, err
                    )

        context.update(self.build_attrs(self.attrs, {
            'name': name,
            'module': 'geodjango_%s' % name.replace('-', '_'),  # JS-safe
            'serialized': self.serialize(value),
            'geom_type': gdal.OGRGeomType(self.attrs['geom_type']),
            'STATIC_URL': settings.STATIC_URL,
            'LANGUAGE_BIDI': translation.get_language_bidi(),
            **(attrs or {}),
        }))
        return context


class OpenLayersWidget(BaseGeometryWidget):
    template_name = 'gis/openlayers.html'
    map_srid = 3857

    class Media:
        css = {
            'all': (
                'https://cdnjs.cloudflare.com/ajax/libs/ol3/4.6.5/ol.css',
                'gis/css/ol3.css',
            )
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/ol3/4.6.5/ol.js',
            'gis/js/OLMapWidget.js',
        )

    def serialize(self, value):
        return value.json if value else ''

    def deserialize(self, value):
        """
        Deserialize a GeoJSON geometry string into a geometry object.
        
        Args:
        value (str): A GeoJSON geometry string.
        
        Returns:
        Geometry: A geometry object with the SRID set based on the map's SRID.
        
        Notes:
        - The function uses the `super().deserialize` method to convert the input string into a geometry object.
        - If the input string matches the GeoJSON format and the map's SRID is not 4326, the SRID
        """

        geom = super().deserialize(value)
        # GeoJSON assumes WGS84 (4326). Use the map's SRID instead.
        if geom and json_regex.match(value) and self.map_srid != 4326:
            geom.srid = self.map_srid
        return geom


class OSMWidget(OpenLayersWidget):
    """
    An OpenLayers/OpenStreetMap-based widget.
    """
    template_name = 'gis/openlayers-osm.html'
    default_lon = 5
    default_lat = 47
    default_zoom = 12

    def __init__(self, attrs=None):
        """
        Initialize a new instance of the class.
        
        Args:
        attrs (dict): Additional attributes to be set on the instance.
        
        This method initializes a new instance of the class by setting default attributes such as `default_lon`, `default_lat`, and `default_zoom`. It then updates these attributes with any additional attributes provided via the `attrs` parameter.
        """

        super().__init__()
        for key in ('default_lon', 'default_lat', 'default_zoom'):
            self.attrs[key] = getattr(self, key)
        if attrs:
            self.attrs.update(attrs)
