from django.db import migrations, models


def raise_error(apps, schema_editor):
    """
    This function is designed to simulate an error during a database migration process. It creates a new instance of the Editor model and then raises a RuntimeError to abort the migration.
    
    Key Parameters:
    - apps: The apps registry used to access models and other components of the application.
    - schema_editor: The schema editor used to perform database operations.
    
    No return value. The function raises a RuntimeError to halt the migration process.
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
