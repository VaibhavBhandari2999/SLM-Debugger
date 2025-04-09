"""
This Python file is part of a Django application that leverages GeoDjango for spatial database operations. It defines two model field classes: `AreaField` and `DistanceField`. These fields are used to store and manipulate spatial data related to areas and distances, respectively. The `AreaField` is designed to handle calculations involving area measurements, while the `DistanceField` is tailored for distance-related computations. Both fields utilize Django's GIS capabilities to ensure accurate and efficient spatial data management.
```python
"""
from django.contrib.gis.db.models.sql.conversion import (
    AreaField, DistanceField,
)

__all__ = [
    'AreaField', 'DistanceField',
]
