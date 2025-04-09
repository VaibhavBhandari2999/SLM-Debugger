"""
```markdown
# This file contains a Django management command for testing label-based commands.
# It defines a single class `Command` which inherits from `LabelCommand` provided by Django.
# The `handle_label` method processes a given label and prints out the label and options passed to it.
# No external dependencies are required other than Django itself.
```

### Explanation:
- **Purpose**: The file serves as a test script for label-based commands in Django.
- **Main Classes**:
  - `Command`: A subclass of `LabelCommand` that handles the execution of label-based commands.
- **Key Responsibilities**:
  - The `handle_label` method is responsible for processing the label and printing the label along with the options passed to
"""
from django.core.management.base import LabelCommand


class Command(LabelCommand):
    help = "Test Label-based commands"
    requires_system_checks = []

    def handle_label(self, label, **options):
        print('EXECUTE:LabelCommand label=%s, options=%s' % (label, sorted(options.items())))
