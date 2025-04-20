from django.db import migrations


def assert_foo_contenttype_not_cached(apps, schema_editor):
    """
    Ensures that the contenttypes_tests.Foo ContentType is not cached.
    
    This function checks if the contenttypes_tests.Foo ContentType is cached. If it is cached, it verifies that the model field of the cached ContentType is set to 'foo'. If the contenttypes_tests.Foo ContentType is not cached, it does nothing. If the contenttypes_tests.Foo ContentType is cached but its model field is not set to 'foo', it raises an AssertionError.
    
    Parameters:
    apps (Apps): The Django
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
