from argparse import ArgumentError

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Adds arguments to the parser.
        
        This function attempts to add a version argument to the parser with the specified version number. If the `--version` argument already exists, it raises a `CommandError`.
        
        Parameters:
        parser (argparse.ArgumentParser): The argument parser to which the argument will be added.
        
        Returns:
        None: This function does not return any value. It either adds the argument to the parser or raises an exception.
        
        Raises:
        CommandError: If the `--version` argument already
        """

        try:
            parser.add_argument("--version", action="version", version="A.B.C")
        except ArgumentError:
            pass
        else:
            raise CommandError("--version argument does no yet exist")

    def handle(self, *args, **options):
        return "Detected that --version already exists"
