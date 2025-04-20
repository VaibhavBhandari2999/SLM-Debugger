import json

from django.contrib.gis.geos import LinearRing, Point, Polygon
from django.core import serializers
from django.test import TestCase

from .models import City, MultiFields, PennsylvaniaCity


class GeoJSONSerializerTests(TestCase):
    fixtures = ['initial']

    def test_builtin_serializers(self):
        """
        'geojson' should be listed in available serializers.
        """
        all_formats = set(serializers.get_serializer_formats())
        public_formats = set(serializers.get_public_serializer_formats())

        self.assertIn('geojson', all_formats),
        self.assertIn('geojson', public_formats)

    def test_serialization_base(self):
        """
        Tests the serialization of City objects into GeoJSON format.
        
        This function serializes all City objects into GeoJSON format and checks the correctness of the serialized data.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function uses the `serializers.serialize` method to convert City objects into GeoJSON.
        - It then loads the serialized data into a JSON object for further inspection.
        - The test verifies that the number of features in the GeoJSON matches the number of City objects
        """

        geojson = serializers.serialize('geojson', City.objects.all().order_by('name'))
        geodata = json.loads(geojson)
        self.assertEqual(len(geodata['features']), len(City.objects.all()))
        self.assertEqual(geodata['features'][0]['geometry']['type'], 'Point')
        self.assertEqual(geodata['features'][0]['properties']['name'], 'Chicago')
        first_city = City.objects.all().order_by('name').first()
        self.assertEqual(geodata['features'][0]['properties']['pk'], str(first_city.pk))

    def test_geometry_field_option(self):
        """
        When a model has several geometry fields, the 'geometry_field' option
        can be used to specify the field to use as the 'geometry' key.
        """
        MultiFields.objects.create(
            city=City.objects.first(), name='Name', point=Point(5, 23),
            poly=Polygon(LinearRing((0, 0), (0, 5), (5, 5), (5, 0), (0, 0))))

        geojson = serializers.serialize('geojson', MultiFields.objects.all())
        geodata = json.loads(geojson)
        self.assertEqual(geodata['features'][0]['geometry']['type'], 'Point')

        geojson = serializers.serialize(
            'geojson',
            MultiFields.objects.all(),
            geometry_field='poly'
        )
        geodata = json.loads(geojson)
        self.assertEqual(geodata['features'][0]['geometry']['type'], 'Polygon')

        # geometry_field is considered even if not in fields (#26138).
        geojson = serializers.serialize(
            'geojson',
            MultiFields.objects.all(),
            geometry_field='poly',
            fields=('city',)
        )
        geodata = json.loads(geojson)
        self.assertEqual(geodata['features'][0]['geometry']['type'], 'Polygon')

    def test_fields_option(self):
        """
        The fields option allows to define a subset of fields to be present in
        the 'properties' of the generated output.
        """
        PennsylvaniaCity.objects.create(name='Mansfield', county='Tioga', point='POINT(-77.071445 41.823881)')
        geojson = serializers.serialize(
            'geojson', PennsylvaniaCity.objects.all(), fields=('county', 'point'),
        )
        geodata = json.loads(geojson)
        self.assertIn('county', geodata['features'][0]['properties'])
        self.assertNotIn('founded', geodata['features'][0]['properties'])
        self.assertNotIn('pk', geodata['features'][0]['properties'])

    def test_srid_option(self):
        """
        Function: test_srid_option
        Summary: Tests the SRID (Spatial Reference ID) option when serializing a queryset of City objects to GeoJSON format.
        Parameters: None
        Key Parameters:
        - None
        
        Keywords:
        - srid: The Spatial Reference ID to use for the GeoJSON output. In this case, it is set to 2847.
        
        Input:
        - A queryset of City objects ordered by their name.
        
        Output:
        - A GeoJSON string with the specified SRID
        """

        geojson = serializers.serialize('geojson', City.objects.all().order_by('name'), srid=2847)
        geodata = json.loads(geojson)
        self.assertEqual(
            [int(c) for c in geodata['features'][0]['geometry']['coordinates']],
            [1564802, 5613214]
        )

    def test_deserialization_exception(self):
        """
        GeoJSON cannot be deserialized.
        """
        with self.assertRaises(serializers.base.SerializerDoesNotExist):
            serializers.deserialize('geojson', '{}')
