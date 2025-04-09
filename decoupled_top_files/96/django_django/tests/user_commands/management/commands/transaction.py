"""
```markdown
# Summary

This Django management command file provides a simple way to greet users with a "Hello!" message. It defines a single command class `Command` which inherits from `BaseCommand` provided by Django's management module.

## Classes

- **Command**: A subclass of `BaseCommand` that overrides the `handle` method to return a greeting message.

## Functions

- **handle**: This method is called when the command is executed. It takes no arguments and returns the string "Hello!".

## Key Responsibilities

- The `handle` method is responsible for generating and returning the greeting message.

## Interactions

- The `Command` class interacts with Django's management framework to define and execute a custom command.
```
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Say hello."
    args = ""
    output_transaction = True

    def handle(self, *args, **options):
        return "Hello!"
