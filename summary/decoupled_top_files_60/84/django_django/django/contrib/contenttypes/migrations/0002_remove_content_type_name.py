from django.db import migrations, models


def add_legacy_name(apps, schema_editor):
    """
    Modifies the 'name' field of all ContentType objects in the database.
    
    This function updates the 'name' field of each ContentType object to reflect the
    object name of the model it represents. If the model cannot be found, the original
    model name is used instead.
    
    Parameters:
    apps (Apps): An instance of the Apps class from Django's apps module, used to
    dynamically load models based on app_label and model.
    schema_editor (SchemaEditor): An instance of the Schema
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
