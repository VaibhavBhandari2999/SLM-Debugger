from django.db import migrations, models


def add_legacy_name(apps, schema_editor):
    """
    Modifies the 'name' field of all ContentType objects to reflect the actual model class name.
    
    This function is designed to update the 'name' field of ContentType objects in a Django application. It retrieves all ContentType objects and attempts to set the 'name' field to the name of the corresponding model class. If the model class cannot be found, it falls back to using the model name directly.
    
    Parameters:
    apps (Apps): The Django Apps registry used to access models dynamically.
    schema_editor (
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
