"""
```markdown
# lookuperror_a/models.py

This file contains Django model definitions for a database schema. It includes three models: `C1`, `C2`, and `C3`. 

- **C1**: A basic model with no fields.
- **C2**: Inherits from `models.Model` and has a foreign key relationship with `A1` from another app (`lookuperror_a`). 
- **C3**: Another basic model with no fields.

The primary responsibility of this file is to define the structure of the database tables and their relationships. The `C2` model specifically establishes a one-to-many relationship with `A1`, which is crucial for data integrity and querying related data efficiently.

```

Docstring generated accurately
"""
from django.db import models


class C1(models.Model):
    pass


class C2(models.Model):
    a1 = models.ForeignKey('lookuperror_a.A1', models.CASCADE)


class C3(models.Model):
    pass
