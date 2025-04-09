"""
```markdown
# This file contains a Django management command for setting a specific value.
# It defines a single class `Command` which extends `BaseCommand` from Django's management module.
# The `add_arguments` method sets up the argument parsing for the command, allowing users to specify a '--set' option.
# The `handle` method processes the input arguments and outputs a message indicating the set value.
```

### Explanation:
- **Purpose**: The file provides a custom Django management command for setting a specific value.
- **Classes**:
  - `Command`: A subclass of `BaseCommand` that defines the behavior of the management command.
- **Functions**:
  - `add_arguments(parser)`: Configures the command-line
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--set')

    def handle(self, **options):
        self.stdout.write('Set %s' % options['set'])
