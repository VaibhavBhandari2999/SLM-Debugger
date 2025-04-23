import json

from django.contrib.gis.gdal import CoordTransform, SpatialReference
from django.core.serializers.base import SerializerDoesNotExist
from django.core.serializers.json import Serializer as JSONSerializer


class Serializer(JSONSerializer):
    """
    Convert a queryset to GeoJSON, http://geojson.org/
    """
    def _init_options(self):
        super()._init_options()
        self.geometry_field = self.json_kwargs.pop('geometry_field', None)
        self.srid = self.json_kwargs.pop('srid', 4326)
        if (self.selected_fields is not None and self.geometry_field is not None and
                self.geometry_field not in self.selected_fields):
            self.selected_fields = [*self.selected_fields, self.geometry_field]

    def start_serialization(self):
        """
        Starts the serialization process for a FeatureCollection in GeoJSON format.
        
        This method initializes the serialization of a GeoJSON FeatureCollection. It writes the initial part of the GeoJSON structure, including the type, CRS (Coordinate Reference System), and an empty features array.
        
        Parameters:
        None
        
        Returns:
        None
        
        Notes:
        - The CRS is specified by the EPSG code stored in `self.srid`.
        - The method writes to `self.stream`, which should be an open file-like
        """

        self._init_options()
        self._cts = {}  # cache of CoordTransform's
        self.stream.write(
            '{"type": "FeatureCollection", "crs": {"type": "name", "properties": {"name": "EPSG:%d"}},'
            ' "features": [' % self.srid)

    def end_serialization(self):
        self.stream.write(']}')

    def start_object(self, obj):
        """
        Start processing an object.
        
        This method is called when the object starts being processed. It initializes the `_geometry` attribute to `None`. If no geometry field is specified, it searches through the object's fields to find the first field that has a `geom_type` attribute and sets it as the `geometry_field`.
        
        Parameters:
        obj (object): The object being processed.
        
        Returns:
        None: This method does not return any value.
        """

        super().start_object(obj)
        self._geometry = None
        if self.geometry_field is None:
            # Find the first declared geometry field
            for field in obj._meta.fields:
                if hasattr(field, 'geom_type'):
                    self.geometry_field = field.name
                    break

    def get_dump_object(self, obj):
        data = {
            "type": "Feature",
            "properties": self._current,
        }
        if ((self.selected_fields is None or 'pk' in self.selected_fields) and
                'pk' not in data["properties"]):
            data["properties"]["pk"] = obj._meta.pk.value_to_string(obj)
        if self._geometry:
            if self._geometry.srid != self.srid:
                # If needed, transform the geometry in the srid of the global geojson srid
                if self._geometry.srid not in self._cts:
                    srs = SpatialReference(self.srid)
                    self._cts[self._geometry.srid] = CoordTransform(self._geometry.srs, srs)
                self._geometry.transform(self._cts[self._geometry.srid])
            data["geometry"] = json.loads(self._geometry.geojson)
        else:
            data["geometry"] = None
        return data

    def handle_field(self, obj, field):
        if field.name == self.geometry_field:
            self._geometry = field.value_from_object(obj)
        else:
            super().handle_field(obj, field)


class Deserializer:
    def __init__(self, *args, **kwargs):
        raise SerializerDoesNotExist("geojson is a serialization-only serializer")
