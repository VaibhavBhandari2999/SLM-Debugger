"""
```markdown
# This file contains a Django management command for setting a specific value.
# It defines a single class `Command` which extends `BaseCommand` from Django's core management module.
# The `add_arguments` method sets up a required argument `--set`.
# The `handle` method processes the provided `--set` argument and outputs it to the console.
#
# Usage: python manage.py set_value --set <value>
#
# The `Command` class is responsible for handling the logic of setting a value via the command line interface.
# It interacts with the Django framework to parse command-line arguments and output messages.
```

### Explanation:
- **Purpose**: The file provides a Django management command for setting a specific value
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--set")

    def handle(self, **options):
        self.stdout.write("Set %s" % options["set"])
