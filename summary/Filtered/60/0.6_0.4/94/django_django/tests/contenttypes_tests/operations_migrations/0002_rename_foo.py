from django.db import migrations


def assert_foo_contenttype_not_cached(apps, schema_editor):
    """
    Ensures that the contenttypes_tests.Foo ContentType is not cached in the database.
    
    This function checks if the contenttypes_tests.Foo ContentType is cached in the database. If the content type does not exist, it passes. If it exists but the model is not set to 'foo', or if the content type is not cached at all, an AssertionError is raised.
    
    Parameters:
    - apps: The apps registry used to access models.
    - schema_editor: The schema editor used to interact with the database
    """

    ContentType = apps.get_model("contenttypes", "ContentType")
    try:
        content_type = ContentType.objects.get_by_natural_key(
            "contenttypes_tests", "foo"
        )
    except ContentType.DoesNotExist:
        pass
    else:
        if not ContentType.objects.filter(
            app_label="contenttypes_tests", model="foo"
        ).exists():
            raise AssertionError(
                "The contenttypes_tests.Foo ContentType should not be cached."
            )
        elif content_type.model != "foo":
            raise AssertionError(
                "The cached contenttypes_tests.Foo ContentType should have "
                "its model set to 'foo'."
            )


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes_tests", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel("Foo", "RenamedFoo"),
        migrations.RunPython(
            assert_foo_contenttype_not_cached, migrations.RunPython.noop
        ),
    ]
