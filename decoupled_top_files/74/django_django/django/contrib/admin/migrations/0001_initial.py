"""
This Python file contains a Django migration script for creating a `LogEntry` model. The `LogEntry` model is designed to log actions performed by users on various objects within the Django admin interface. The migration specifies dependencies and fields for the `LogEntry` model, including timestamps, user information, object representation, action flags, and change messages. The model is ordered by action time and stored in the database table `django_admin_log`. The `LogEntry` model also includes a custom manager class for managing log entries.
Certainly! Here's a concise and informative docstring based on the provided Python file:

```python
"""
import django.contrib.admin.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action_time', models.DateTimeField(auto_now=True, verbose_name='action time')),
                ('object_id', models.TextField(null=True, verbose_name='object id', blank=True)),
                ('object_repr', models.CharField(max_length=200, verbose_name='object repr')),
                ('action_flag', models.PositiveSmallIntegerField(verbose_name='action flag')),
                ('change_message', models.TextField(verbose_name='change message', blank=True)),
                ('content_type', models.ForeignKey(
                    on_delete=models.SET_NULL,
                    blank=True, null=True,
                    to='contenttypes.ContentType',
                    verbose_name='content type',
                )),
                ('user', models.ForeignKey(
                    to=settings.AUTH_USER_MODEL,
                    on_delete=models.CASCADE,
                    verbose_name='user',
                )),
            ],
            options={
                'ordering': ['-action_time'],
                'db_table': 'django_admin_log',
                'verbose_name': 'log entry',
                'verbose_name_plural': 'log entries',
            },
            bases=(models.Model,),
            managers=[
                ('objects', django.contrib.admin.models.LogEntryManager()),
            ],
        ),
    ]
