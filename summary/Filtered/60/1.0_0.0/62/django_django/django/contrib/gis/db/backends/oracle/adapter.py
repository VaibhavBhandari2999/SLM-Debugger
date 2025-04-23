from cx_Oracle import CLOB

from django.contrib.gis.db.backends.base.adapter import WKTAdapter
from django.contrib.gis.geos import GeometryCollection, Polygon


class OracleSpatialAdapter(WKTAdapter):
    input_size = CLOB

    def __init__(self, geom):
        """
        Oracle requires that polygon rings are in proper orientation. This
        affects spatial operations and an invalid orientation may cause
        failures. Correct orientations are:
         * Outer ring - counter clockwise
         * Inner ring(s) - clockwise
        """
        if isinstance(geom, Polygon):
            if self._polygon_must_be_fixed(geom):
                geom = self._fix_polygon(geom)
        elif isinstance(geom, GeometryCollection):
            if any(isinstance(g, Polygon) and self._polygon_must_be_fixed(g) for g in geom):
                geom = self._fix_geometry_collection(geom)

        self.wkt = geom.wkt
        self.srid = geom.srid

    @staticmethod
    def _polygon_must_be_fixed(poly):
        """
        Determine if a polygon needs to be fixed.
        
        This function checks if a given polygon needs to be fixed. A polygon needs to be fixed if it is not empty and either its exterior ring is not counterclockwise or any of its interior rings are not counterclockwise.
        
        Parameters:
        poly (shapely.geometry.Polygon): The polygon to check.
        
        Returns:
        bool: True if the polygon needs to be fixed, False otherwise.
        """

        return (
            not poly.empty and
            (
                not poly.exterior_ring.is_counterclockwise or
                any(x.is_counterclockwise for x in poly)
            )
        )

    @classmethod
    def _fix_polygon(cls, poly, clone=True):
        """Fix single polygon orientation as described in __init__()."""
        if clone:
            poly = poly.clone()

        if not poly.exterior_ring.is_counterclockwise:
            poly.exterior_ring = list(reversed(poly.exterior_ring))

        for i in range(1, len(poly)):
            if poly[i].is_counterclockwise:
                poly[i] = list(reversed(poly[i]))

        return poly

    @classmethod
    def _fix_geometry_collection(cls, coll):
        """
        Fix polygon orientations in geometry collections as described in
        __init__().
        """
        coll = coll.clone()
        for i, geom in enumerate(coll):
            if isinstance(geom, Polygon):
                coll[i] = cls._fix_polygon(geom, clone=False)
        return coll
