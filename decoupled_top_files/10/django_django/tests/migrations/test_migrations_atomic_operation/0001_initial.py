from django.db import migrations, models


def raise_error(apps, schema_editor):
    """
    Raises a runtime error during a non-atomic migration, creating an editor instance beforehand.
    
    This function is designed to test the behavior of atomic operations within non-atomic migrations. It creates an instance of the `Editor` model using the provided `apps` and `schema_editor` objects, then raises a `RuntimeError` with the message 'Abort migration'.
    
    Args:
    apps (django.apps.registry.Apps): The application registry containing the models.
    schema_editor (django.db.migrations.state
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
