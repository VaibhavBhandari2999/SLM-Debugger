from django.db import migrations, models


def raise_error(apps, schema_editor):
    """
    Function to raise an error during a database migration. This function is designed to be used within a Django migration file to test the handling of non-atomic operations.
    
    Key Parameters:
    - apps: The apps registry used to access models and other components.
    - schema_editor: The schema editor used to execute database operations.
    
    Returns:
    None: This function does not return a value. It is intended to raise a RuntimeError to abort the migration process.
    
    Note:
    This function is intended for testing purposes and should not
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
