from django.db import migrations, models


def add_legacy_name(apps, schema_editor):
    """
    Modifies the 'name' field of all ContentType objects by setting it to the object name of the model it represents. This function is designed to be used in a Django migration.
    
    Parameters:
    apps (Apps): The Django Apps registry to use for model discovery.
    schema_editor (SchemaEditor): The schema editor to use for database operations.
    
    Returns:
    None: This function modifies the database in place and does not return any value.
    """

    ContentType = apps.get_model('contenttypes', 'ContentType')
    for ct in ContentType.objects.all():
        try:
            ct.name = apps.get_model(ct.app_label, ct.model)._meta.object_name
        except LookupError:
            ct.name = ct.model
        ct.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contenttype',
            options={'verbose_name': 'content type', 'verbose_name_plural': 'content types'},
        ),
        migrations.AlterField(
            model_name='contenttype',
            name='name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.RunPython(
            migrations.RunPython.noop,
            add_legacy_name,
            hints={'model_name': 'contenttype'},
        ),
        migrations.RemoveField(
            model_name='contenttype',
            name='name',
        ),
    ]
