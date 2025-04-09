"""
The provided Python file is part of a Django project that extends the functionality of Django's database models to support geographic information system (GIS) data. It imports and redefines several GIS-related fields and aggregate functions from `django.contrib.gis.db.models` and includes them in the module's public API.

#### Classes and Functions:
- **Classes**:
  - `GeometryCollectionField`, `GeometryField`, `LineStringField`, `MultiLineStringField`, `MultiPointField`, `MultiPolygonField`, `PointField`, `PolygonField`, `RasterField`: These are custom GIS field types that allow storing various geometric shapes and raster data in a Django model.
  
- **Functions**:
  - No specific functions are defined in this file
"""
from django.db.models import *  # NOQA isort:skip
from django.db.models import __all__ as models_all  # isort:skip
import django.contrib.gis.db.models.functions  # NOQA
import django.contrib.gis.db.models.lookups  # NOQA
from django.contrib.gis.db.models.aggregates import *  # NOQA
from django.contrib.gis.db.models.aggregates import __all__ as aggregates_all
from django.contrib.gis.db.models.fields import (
    GeometryCollectionField, GeometryField, LineStringField,
    MultiLineStringField, MultiPointField, MultiPolygonField, PointField,
    PolygonField, RasterField,
)

__all__ = models_all + aggregates_all
__all__ += [
    'GeometryCollectionField', 'GeometryField', 'LineStringField',
    'MultiLineStringField', 'MultiPointField', 'MultiPolygonField', 'PointField',
    'PolygonField', 'RasterField',
]
