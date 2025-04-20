from django.db import migrations, models


def raise_error(apps, schema_editor):
    """
    Generates a migration function that raises a runtime error.
    
    This function is intended to be used within Django migrations. It creates an instance of the Editor model and then raises a RuntimeError to abort the migration process. The function is wrapped in a transaction to ensure that the partial migration does not leave the database in an inconsistent state.
    
    Parameters:
    apps (Apps): The Django Apps registry to access model classes.
    schema_editor (SchemaEditor): The SchemaEditor to make changes to the database schema.
    
    Returns:
    """

    # Test atomic operation in non-atomic migration is wrapped in transaction
    Editor = apps.get_model("migrations", "Editor")
    Editor.objects.create(name="Test Editor")
    raise RuntimeError("Abort migration")


class Migration(migrations.Migration):
    atomic = False

    operations = [
        migrations.CreateModel(
            "Editor",
            [
                ("name", models.CharField(primary_key=True, max_length=255)),
            ],
        ),
        migrations.RunPython(raise_error, reverse_code=raise_error, atomic=True),
    ]
