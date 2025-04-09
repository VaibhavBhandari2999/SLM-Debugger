"""
```markdown
# This file contains a Django management command that processes a list of integers provided as an argument.
# It demonstrates how to define and use custom management commands in Django projects.
#
# Classes:
# - Command: A subclass of `BaseCommand` that defines the behavior of the management command.
#
# Functions:
# - add_arguments: Adds the "--foo-list" argument to the command, which expects a list of integers.
# - handle: Processes the arguments passed to the command and prints them to the console.
#
# The `handle` method iterates over the options dictionary, which contains the parsed command-line arguments,
# and writes each key-value pair to the standard output. This allows for easy debugging and testing of the command
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--foo-list", nargs="+", type=int, required=True)

    def handle(self, *args, **options):
        for option, value in options.items():
            self.stdout.write("%s=%s" % (option, value))
