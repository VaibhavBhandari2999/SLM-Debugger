"""
```markdown
This Django management command checks for the existence of the `--version` argument in the provided argument parser. If the `--version` argument does not exist, it adds it with a specific version number. If it does exist, it raises a `CommandError`. The `handle` method returns a message indicating the outcome of the check.
```

### Docstring:
```python
"""
from argparse import ArgumentError

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Adds command-line arguments to the parser.
        
        Args:
        parser (ArgumentParser): The argument parser to which the arguments will be added.
        
        Raises:
        CommandError: If the --version argument already exists in the parser.
        """

        try:
            parser.add_argument('--version', action='version', version='A.B.C')
        except ArgumentError:
            pass
        else:
            raise CommandError('--version argument does no yet exist')

    def handle(self, *args, **options):
        return 'Detected that --version already exists'
