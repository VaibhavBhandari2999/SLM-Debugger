from django.db import migrations, models


def raise_error(apps, schema_editor):
    """
    This function is designed to raise a RuntimeError during a database migration, simulating an error scenario. It is intended to be used in a non-atomic migration where operations are not wrapped in a transaction.
    
    Parameters:
    apps (Apps): An instance of the Django Apps API, used to access models by their app and model names.
    schema_editor (SchemaEditor): An instance of the SchemaEditor class, used to make changes to the database schema.
    
    Returns:
    None: The function does not return
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
