"""
```markdown
This Django management command creates a new project directory structure. It generates a random SECRET_KEY and includes it in the project's settings. The `Command` class extends `TemplateCommand` from Django's core management templates. The `handle` method is responsible for creating the project, setting up the directory, and passing necessary parameters to the superclass method.
```

### Detailed Docstring:
```python
"""
from django.core.management.templates import TemplateCommand

from ..utils import get_random_secret_key


class Command(TemplateCommand):
    help = (
        "Creates a Django project directory structure for the given project "
        "name in the current directory or optionally in the given directory."
    )
    missing_args_message = "You must provide a project name."

    def handle(self, **options):
        """
        Generates a Django project with the specified name and directory. Creates a random SECRET_KEY and passes it to the super().handle() method along with other options.
        
        Args:
        name (str): The name of the Django project.
        directory (str): The directory where the project will be created.
        
        Returns:
        None
        """

        project_name = options.pop('name')
        target = options.pop('directory')

        # Create a random SECRET_KEY to put it in the main settings.
        options['secret_key'] = get_random_secret_key()

        super().handle('project', project_name, target, **options)
