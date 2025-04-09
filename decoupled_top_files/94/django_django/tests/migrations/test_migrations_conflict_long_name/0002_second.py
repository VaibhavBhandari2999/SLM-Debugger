"""
```markdown
# migrations/0002_create_something.py

This Django migration script creates a new model `Something` with an auto-incrementing primary key.

## Classes Defined
- **Migration**: A subclass of `django.db.migrations.Migration` representing a database migration.
  - **Dependencies**: Specifies the previous migration this one depends on.
  - **Operations**: Contains the operation to create the `Something` model.

## Functions Defined
- None

## Key Responsibilities
- Defines a new model `Something` with an auto-incrementing primary key.

## Interactions
- This migration relies on the initial migration `0001_initial` to be applied first.
```

### Explanation:
- The docstring
"""
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("migrations", "0001_initial")]

    operations = [
        migrations.CreateModel(
            "Something",
            [
                ("id", models.AutoField(primary_key=True)),
            ],
        ),
    ]
