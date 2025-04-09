from django.db import migrations, models


def raise_error(apps, schema_editor):
    """
    Raises a runtime error during a non-atomic migration by creating a Publisher instance and then intentionally aborting the process.
    
    This function is designed to be used within a Django migration file. It creates an instance of the `Publisher` model and then raises a `RuntimeError` to halt the migration process. The `Publisher` model is retrieved using `apps.get_model`, indicating that this function operates on a specific app's models.
    
    Args:
    apps (django.apps.registry.Apps): The application
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
