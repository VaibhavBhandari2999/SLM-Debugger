from django.contrib.gis.db.models import F, GeometryField, Value, functions
from django.contrib.gis.geos import Point, Polygon
from django.db import connection
from django.db.models import Count, Min
from django.test import TestCase, skipUnlessDBFeature

from .models import City, ManyPointModel, MultiFields


class GeoExpressionsTests(TestCase):
    fixtures = ['initial']

    def test_geometry_value_annotation(self):
        """
        Annotate a City object with a Point geometry value and verify that the annotated value matches the original Point object.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Elements:
        - p: A Point object with specified coordinates and SRID (Spatial Reference System Identifier).
        - City: A Django model representing a city with a geometry field.
        - Value: A function from Django's F expressions that allows the use of model field values in annotations.
        - GeometryField: A Django field
        """

        p = Point(1, 1, srid=4326)
        point = City.objects.annotate(p=Value(p, GeometryField(srid=4326))).first().p
        self.assertEqual(point, p)

    @skipUnlessDBFeature('supports_transform')
    def test_geometry_value_annotation_different_srid(self):
        p = Point(1, 1, srid=32140)
        point = City.objects.annotate(p=Value(p, GeometryField(srid=4326))).first().p
        self.assertTrue(point.equals_exact(p.transform(4326, clone=True), 10 ** -5))
        self.assertEqual(point.srid, 4326)

    @skipUnlessDBFeature('supports_geography')
    def test_geography_value(self):
        """
        Tests the area calculation of a geography Polygon field in a City model.
        
        This function creates a Polygon object and uses it to annotate a City model instance with the area of the polygon in square kilometers. The area is calculated using the Area function from Django's database functions, which is applied to a Value object representing the polygon with a geography=True flag. The result is then compared to a known value (12305.1 square kilometers) with an absolute tolerance of 0.
        
        Parameters:
        """

        p = Polygon(((1, 1), (1, 2), (2, 2), (2, 1), (1, 1)))
        area = City.objects.annotate(a=functions.Area(Value(p, GeometryField(srid=4326, geography=True)))).first().a
        self.assertAlmostEqual(area.sq_km, 12305.1, 0)

    def test_update_from_other_field(self):
        """
        Updates the 'point2' and 'point3' fields of a ManyPointModel instance based on the 'point1' field. The function performs two updates:
        1. Updates 'point2' to be the same as 'point1', ensuring both points have the same SRID.
        2. Updates 'point3' to be the same as 'point1', but ensures the updated point has a different SRID (3857).
        
        Parameters:
        - None (the function uses the database
        """

        p1 = Point(1, 1, srid=4326)
        p2 = Point(2, 2, srid=4326)
        obj = ManyPointModel.objects.create(
            point1=p1,
            point2=p2,
            point3=p2.transform(3857, clone=True),
        )
        # Updating a point to a point of the same SRID.
        ManyPointModel.objects.filter(pk=obj.pk).update(point2=F('point1'))
        obj.refresh_from_db()
        self.assertEqual(obj.point2, p1)
        # Updating a point to a point with a different SRID.
        if connection.features.supports_transform:
            ManyPointModel.objects.filter(pk=obj.pk).update(point3=F('point1'))
            obj.refresh_from_db()
            self.assertTrue(obj.point3.equals_exact(p1.transform(3857, clone=True), 0.1))

    def test_multiple_annotation(self):
        multi_field = MultiFields.objects.create(
            point=Point(1, 1),
            city=City.objects.get(name='Houston'),
            poly=Polygon(((1, 1), (1, 2), (2, 2), (2, 1), (1, 1))),
        )
        qs = City.objects.values('name').annotate(
            distance=Min(functions.Distance('multifields__point', multi_field.city.point)),
        ).annotate(count=Count('multifields'))
        self.assertTrue(qs.first())

    @skipUnlessDBFeature('has_Translate_function')
    def test_update_with_expression(self):
        """
        Update the 'point' field of a City object with a translated geometry.
        
        This function creates a City object with an initial point at coordinates (1, 1) and SRID 4326. It then updates the 'point' field using the Translate function to shift the point by 1 unit in both the x and y directions. After the update, the function refreshes the City object from the database and asserts that the new point is at coordinates (2, 2)
        """

        city = City.objects.create(point=Point(1, 1, srid=4326))
        City.objects.filter(pk=city.pk).update(point=functions.Translate('point', 1, 1))
        city.refresh_from_db()
        self.assertEqual(city.point, Point(2, 2, srid=4326))
