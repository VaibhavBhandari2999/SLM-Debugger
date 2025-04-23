from django.db import migrations, models


def raise_error(apps, schema_editor):
    """
    Function to raise an error during a database migration.
    
    This function is designed to be used within a Django migration. It attempts to create a new Publisher object and then raises a RuntimeError to abort the migration. The function operates within a non-atomic migration context, meaning it is not wrapped in a transaction.
    
    Parameters:
    apps (django.apps.registry.Apps): The application registry used to access model classes.
    schema_editor (django.db.backends.base.schema.BaseSchemaEditor): The schema editor used to make changes
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
