import json

from django.contrib.gis.gdal import CoordTransform, SpatialReference
from django.core.serializers.base import SerializerDoesNotExist
from django.core.serializers.json import Serializer as JSONSerializer


class Serializer(JSONSerializer):
    """
    Convert a queryset to GeoJSON, http://geojson.org/
    """
    def _init_options(self):
        """
        Initialize the options for the object.
        
        This method is called during the initialization of the object to set up its options. It first calls the parent class's `_init_options` method. Then, it processes the `json_kwargs` dictionary to extract and set the `geometry_field` and `srid` attributes. If `selected_fields` is provided and `geometry_field` is also specified, and `geometry_field` is not already in `selected_fields`, it appends `geometry_field` to `
        """

        super()._init_options()
        self.geometry_field = self.json_kwargs.pop('geometry_field', None)
        self.srid = self.json_kwargs.pop('srid', 4326)
        if (self.selected_fields is not None and self.geometry_field is not None and
                self.geometry_field not in self.selected_fields):
            self.selected_fields = [*self.selected_fields, self.geometry_field]

    def start_serialization(self):
        self._init_options()
        self._cts = {}  # cache of CoordTransform's
        self.stream.write(
            '{"type": "FeatureCollection", "crs": {"type": "name", "properties": {"name": "EPSG:%d"}},'
            ' "features": [' % self.srid)

    def end_serialization(self):
        self.stream.write(']}')

    def start_object(self, obj):
        """
        Starts processing a new object.
        
        This method is called when a new object is being processed. It initializes the geometry field to None and sets the geometry field name if it is not already defined. The geometry field name is determined by searching through the object's fields for the first field that has a `geom_type` attribute.
        
        Parameters:
        obj (object): The object being processed.
        
        Returns:
        None: This method does not return any value.
        
        Attributes:
        geometry_field (str): The name
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
        """
        Handle a field from a Django model object.
        
        This method processes a field from a Django model object. It checks if the field is the geometry field specified in the class. If it is, it assigns the field's value to the instance's `_geometry` attribute. Otherwise, it delegates the handling to the superclass's `handle_field` method.
        
        Parameters:
        obj (django.db.models.Model): The Django model object from which to retrieve the field value.
        field (django.db.models.Field): The
        """

        if field.name == self.geometry_field:
            self._geometry = field.value_from_object(obj)
        else:
            super().handle_field(obj, field)


class Deserializer:
    def __init__(self, *args, **kwargs):
        raise SerializerDoesNotExist("geojson is a serialization-only serializer")
sNotExist("geojson is a serialization-only serializer")
