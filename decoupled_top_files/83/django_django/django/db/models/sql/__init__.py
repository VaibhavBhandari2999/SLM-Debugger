"""
This file appears to be part of a Django application, specifically dealing with SQL query construction. It imports and re-exports the `Query` class from `django.db.models.sql.query` and two submodules (`subqueries` and `where`). It also defines the logical operators `AND` and `OR` for use in constructing SQL queries.

### Docstring:
```python
"""
from django.db.models.sql.query import *  # NOQA
from django.db.models.sql.query import Query
from django.db.models.sql.subqueries import *  # NOQA
from django.db.models.sql.where import AND, OR

__all__ = ['Query', 'AND', 'OR']
