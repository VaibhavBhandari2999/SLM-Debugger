from django.db import migrations, models


def raise_error(apps, schema_editor):
    """
    Function to raise an error during a database migration. This function is intended to test the handling of non-atomic operations within a migration. It creates a new Editor object and then raises a RuntimeError to abort the migration.
    
    Parameters:
    apps (module): The apps registry to access model classes and other components.
    schema_editor (class instance): The schema editor to perform database operations.
    
    Returns:
    None: The function does not return any value but raises a RuntimeError to abort the migration.
    
    Key Points:
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
