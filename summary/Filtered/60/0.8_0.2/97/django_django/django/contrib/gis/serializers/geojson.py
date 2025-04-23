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
        Starts the serialization process for a FeatureCollection in GeoJSON format.
        
        This method initializes the serialization of a FeatureCollection in GeoJSON format. It sets up the necessary context for the serialization, including the Coordinate Reference System (CRS) and a cache for coordinate transformations. The CRS is specified by the SRID (Spatial Reference ID).
        
        Parameters:
        None
        
        Returns:
        None
        
        Notes:
        - The SRID is used to define the CRS in the GeoJSON output.
        - The method
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
        super().start_object(obj)
        self._geometry = None
        if self.geometry_field is None:
            # Find the first declared geometry field
            for field in obj._meta.fields:
                if hasattr(field, "geom_type"):
                    self.geometry_field = field.name
                    break

    def get_dump_object(self, obj):
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
        Handle a field from an object.
        
        This method is used to process fields from a given object. It specifically checks if the field is the geometry field. If it is, the geometry value is stored in the `_geometry` attribute. Otherwise, it delegates the handling of the field to the superclass's `handle_field` method.
        
        Parameters:
        obj (object): The object from which to retrieve the field value.
        field (Field): The field object containing the field name and value.
        
        Returns:
        """

        if field.name == self.geometry_field:
            self._geometry = field.value_from_object(obj)
        else:
            super().handle_field(obj, field)


class Deserializer:
    def __init__(self, *args, **kwargs):
        raise SerializerDoesNotExist("geojson is a serialization-only serializer")
