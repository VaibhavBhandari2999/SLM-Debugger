from django.db import migrations, models


def raise_error(apps, schema_editor):
    """
    Function to raise an error during a database migration.
    
    This function is designed to be used in a Django migration. It attempts to create a new Publisher object and then raises a RuntimeError to abort the migration.
    
    Parameters:
    apps (Apps): The Django Apps API instance, which provides access to models and other components in the application registry.
    schema_editor (SchemaEditor): The SchemaEditor instance, which is used to make changes to the database schema.
    
    Returns:
    None: This function does not return any
    """

    # Test operation in non-atomic migration is not wrapped in transaction
    Publisher = apps.get_model("migrations", "Publisher")
    Publisher.objects.create(name="Test Publisher")
    raise RuntimeError("Abort migration")


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
                (
                    "publisher",
                    models.ForeignKey(
                        "migrations.Publisher", models.SET_NULL, null=True
                    ),
                ),
            ],
        ),
    ]
