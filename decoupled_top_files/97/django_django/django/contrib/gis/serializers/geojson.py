"""
The provided Python file contains custom Django serializers for converting Django model instances to and from GeoJSON format. Specifically, it defines a `Serializer` class that extends Django's built-in `JSONSerializer` to handle GeoJSON serialization, and a `Deserializer` class that raises an exception indicating that deserialization is not supported.

#### Key Components:
1. **Serializer Class**:
   - **Purpose**: Converts Django model instances to GeoJSON format.
   - **Responsibilities**:
     - Initializes options for serialization.
     - Manages the creation of a GeoJSON FeatureCollection.
     - Serializes individual model instances into GeoJSON Features.
   - **Methods**:
     - `_init_options`: Sets up initial options for serialization.
     - `start
"""
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
        Initializes the options for the object.
        
        This method sets up the initial configuration by calling the superclass's `_init_options` method and then populates several fields with values from `json_kwargs`. It also ensures that the `geometry_field` is included in the `selected_fields` list if it is not already present.
        
        Args:
        self: The instance of the class.
        
        Attributes:
        geometry_field (str): The name of the field containing the geometry data.
        id_field (str
        """

        super()._init_options()
        self.geometry_field = self.json_kwargs.pop("geometry_field", None)
        self.id_field = self.json_kwargs.pop("id_field", None)
        self.srid = self.json_kwargs.pop("srid", 4326)
        if (
            self.selected_fields is not None
            and self.geometry_field is not None
            and self.geometry_field not in self.selected_fields
        ):
            self.selected_fields = [*self.selected_fields, self.geometry_field]

    def start_serialization(self):
        """
        Start serializing a GeoJSON FeatureCollection.
        
        This method initializes the serialization process by setting up the necessary options and creating a cache for `CoordTransform` objects. It writes the initial structure of a GeoJSON FeatureCollection to the stream, including the CRS (Coordinate Reference System) information.
        
        Args:
        None
        
        Returns:
        None
        
        Notes:
        - The method writes the following to the stream:
        - `"type": "FeatureCollection"`
        - `"crs":
        """

        self._init_options()
        self._cts = {}  # cache of CoordTransform's
        self.stream.write(
            '{"type": "FeatureCollection", '
            '"crs": {"type": "name", "properties": {"name": "EPSG:%d"}},'
            ' "features": [' % self.srid
        )

    def end_serialization(self):
        self.stream.write("]}")

    def start_object(self, obj):
        """
        Starts processing an object.
        
        This method initializes the `_geometry` attribute to `None`. If no geometry field is explicitly specified, it searches through the object's fields to find the first one with a `geom_type` attribute, setting that as the `geometry_field`.
        
        Args:
        obj (object): The object being processed.
        
        Returns:
        None: This method does not return any value.
        """

        super().start_object(obj)
        self._geometry = None
        if self.geometry_field is None:
            # Find the first declared geometry field
            for field in obj._meta.fields:
                if hasattr(field, "geom_type"):
                    self.geometry_field = field.name
                    break

    def get_dump_object(self, obj):
        """
        Generates a GeoJSON Feature object from a Django model instance.
        
        Args:
        obj (Model): The Django model instance to be converted into a GeoJSON Feature.
        
        Returns:
        dict: A dictionary representing a GeoJSON Feature with properties and geometry based on the provided model instance.
        
        Keyword Arguments:
        - id_field (str, optional): The name of the field to use as the feature's ID. Defaults to `None`.
        - selected_fields (list, optional): A list
        """

        data = {
            "type": "Feature",
            "id": obj.pk if self.id_field is None else getattr(obj, self.id_field),
            "properties": self._current,
        }
        if (
            self.selected_fields is None or "pk" in self.selected_fields
        ) and "pk" not in data["properties"]:
            data["properties"]["pk"] = obj._meta.pk.value_to_string(obj)
        if self._geometry:
            if self._geometry.srid != self.srid:
                # If needed, transform the geometry in the srid of the global
                # geojson srid.
                if self._geometry.srid not in self._cts:
                    srs = SpatialReference(self.srid)
                    self._cts[self._geometry.srid] = CoordTransform(
                        self._geometry.srs, srs
                    )
                self._geometry.transform(self._cts[self._geometry.srid])
            data["geometry"] = json.loads(self._geometry.geojson)
        else:
            data["geometry"] = None
        return data

    def handle_field(self, obj, field):
        """
        Handles the processing of fields for an object.
        
        This method processes each field of an object. If the field name matches
        the geometry field specified in the class, it sets the `_geometry` attribute
        to the value of that field. Otherwise, it delegates the handling of the field
        to the superclass's `handle_field` method.
        
        Args:
        obj (object): The object whose fields are being processed.
        field (Field): The field object representing the current field being
        """

        if field.name == self.geometry_field:
            self._geometry = field.value_from_object(obj)
        else:
            super().handle_field(obj, field)


class Deserializer:
    def __init__(self, *args, **kwargs):
        raise SerializerDoesNotExist("geojson is a serialization-only serializer")
