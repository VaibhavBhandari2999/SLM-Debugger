"""
```markdown
# This migration script adds a new field to an existing Django model.
# It uses PostgreSQL's ArrayField to store integer arrays.
# The migration is part of a series of database schema changes for a project.
```

### Detailed Docstring:
```python
"""
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('postgres_tests', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='integerarraydefaultmodel',
            name='field_2',
            field=django.contrib.postgres.fields.ArrayField(models.IntegerField(), default=[], size=None),
            preserve_default=False,
        ),
    ]
