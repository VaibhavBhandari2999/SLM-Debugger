"""
This Python file contains custom Django model field and utility class definitions. It introduces `ArraySubquery`, a subclass of Django's `Subquery` that returns an array of values from a subquery. The `output_field` property is cached to ensure efficient field handling. This customization allows for more flexible querying capabilities when working with PostgreSQL's array fields in Django models.
```python
"""
from django.contrib.postgres.fields import ArrayField
from django.db.models import Subquery
from django.utils.functional import cached_property


class ArraySubquery(Subquery):
    template = 'ARRAY(%(subquery)s)'

    def __init__(self, queryset, **kwargs):
        super().__init__(queryset, **kwargs)

    @cached_property
    def output_field(self):
        return ArrayField(self.query.output_field)
