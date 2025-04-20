from django.db import migrations, models


def raise_error(apps, schema_editor):
    """
    Function to raise an error during a database migration.
    
    This function is designed to be used within a Django migration file. It creates a new Publisher instance with the name 'Test Publisher' and then raises a RuntimeError to abort the migration process.
    
    Parameters:
    apps (django.apps.apps.Apps): The Django apps registry used to access models.
    schema_editor (django.db.migrations.state.SchemaEditorState): The schema editor used to make changes to the database schema.
    
    Returns:
    None: This function does
    """

    # Test operation in non-atomic migration is not wrapped in transaction
    Publisher = apps.get_model('migrations', 'Publisher')
    Publisher.objects.create(name='Test Publisher')
    raise RuntimeError('Abort migration')


class Migration(migrations.Migration):
    atomic = False

    operations = [
        migrations.CreateModel(
            "Publisher",
            [
                ("name", models.CharField(primary_key=True, max_length=255)),
            ],
        ),
        migrations.RunPython(raise_error),
        migrations.CreateModel(
            "Book",
            [
                ("title", models.CharField(primary_key=True, max_length=255)),
                ("publisher", models.ForeignKey("migrations.Publisher", models.SET_NULL, null=True)),
            ],
        ),
    ]
