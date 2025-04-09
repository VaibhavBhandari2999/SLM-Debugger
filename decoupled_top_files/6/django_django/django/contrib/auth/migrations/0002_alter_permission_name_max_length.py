"""
```markdown
# This migration alters the 'name' field of the 'Permission' model in the Django authentication app.
# It changes the max length of the 'name' field to 255 characters and sets a verbose name for it.
```

### Docstring:
```python
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='name',
            field=models.CharField(max_length=255, verbose_name='name'),
        ),
    ]
