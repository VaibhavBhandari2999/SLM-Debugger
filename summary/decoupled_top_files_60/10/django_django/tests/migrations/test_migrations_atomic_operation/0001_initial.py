from django.db import migrations, models


def raise_error(apps, schema_editor):
    """
    Function to raise an error during a database migration.
    
    This function is intended to be used within a Django migration file to test the handling of non-atomic operations. It creates a new record in the 'Editor' model and then raises a RuntimeError to abort the migration.
    
    Parameters:
    apps (Apps): The Django apps registry used to access model classes.
    schema_editor (SchemaEditor): The schema editor used to make changes to the database schema.
    
    Returns:
    None: This function does not return any
    """

    # Test atomic operation in non-atomic migration is wrapped in transaction
    Editor = apps.get_model('migrations', 'Editor')
    Editor.objects.create(name='Test Editor')
    raise RuntimeError('Abort migration')


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
