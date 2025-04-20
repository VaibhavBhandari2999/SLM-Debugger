from django.db import migrations


def assert_foo_contenttype_not_cached(apps, schema_editor):
    """
    Assert that the contenttypes_tests.Foo ContentType is not cached.
    
    This function checks if the contenttypes_tests.Foo ContentType is cached. If it is cached, it raises an AssertionError. The function uses the ContentType model to check the existence and attributes of the content type.
    
    Parameters:
    apps (Apps): The Django Apps registry to use for model discovery.
    schema_editor (SchemaEditor): The schema editor to use for database operations.
    
    Returns:
    None: The function does not return any value.
    """

    ContentType = apps.get_model('contenttypes', 'ContentType')
    try:
        content_type = ContentType.objects.get_by_natural_key('contenttypes_tests', 'foo')
    except ContentType.DoesNotExist:
        pass
    else:
        if not ContentType.objects.filter(app_label='contenttypes_tests', model='foo').exists():
            raise AssertionError('The contenttypes_tests.Foo ContentType should not be cached.')
        elif content_type.model != 'foo':
            raise AssertionError(
                "The cached contenttypes_tests.Foo ContentType should have "
                "its model set to 'foo'."
            )


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes_tests', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel('Foo', 'RenamedFoo'),
        migrations.RunPython(assert_foo_contenttype_not_cached, migrations.RunPython.noop)
    ]
