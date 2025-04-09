"""
```markdown
# migrations/0002_create_something_else.py

This Django migration script creates a new model `SomethingElse` with an auto-incrementing primary key.

## Classes Defined
- **Migration**: A subclass of `django.db.migrations.Migration` representing a database migration.
  - **Dependencies**: Specifies the dependencies for this migration.
  - **Operations**: Contains the operation to create the `SomethingElse` model.

## Functions Defined
- None

## Key Responsibilities
- Defines a migration to add the `SomethingElse` model to the database schema.

## Interactions
- This migration depends on the initial migration (`0001_initial`) and performs a single operation to create the `SomethingElse` model
"""
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("migrations", "0001_initial")]

    operations = [
        migrations.CreateModel(
            "SomethingElse",
            [
                ("id", models.AutoField(primary_key=True)),
            ],
        ),
    ]
