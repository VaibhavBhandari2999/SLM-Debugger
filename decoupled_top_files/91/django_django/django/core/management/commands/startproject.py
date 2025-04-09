"""
```markdown
# Summary

This Python script is designed to create a new Django project by generating the necessary directory structure and configuration files. It leverages Django's `TemplateCommand` class to facilitate the creation process. The script ensures that a secure `SECRET_KEY` is generated and included in the project's settings.

### Classes Defined

- **Command**: A subclass of `TemplateCommand` tailored for creating Django projects. It overrides the `handle` method to customize the project creation process, including setting up a secure `SECRET_KEY`.

### Functions Defined

- **handle(self, **options)**: This method is responsible for creating a new Django project. It generates a random `SECRET_KEY`, adds it to the project's settings, and then calls
"""
from django.core.checks.security.base import SECRET_KEY_INSECURE_PREFIX
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
        Generates a new Django project with the specified name and directory. Creates a random SECRET_KEY and includes it in the project's settings. Calls the superclass method 'handle' with the appropriate arguments.
        """

        project_name = options.pop('name')
        target = options.pop('directory')

        # Create a random SECRET_KEY to put it in the main settings.
        options['secret_key'] = SECRET_KEY_INSECURE_PREFIX + get_random_secret_key()

        super().handle('project', project_name, target, **options)
