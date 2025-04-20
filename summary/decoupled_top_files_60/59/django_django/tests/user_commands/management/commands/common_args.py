from argparse import ArgumentError

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Function to add command-line arguments to a parser.
        
        This function attempts to add a '--version' argument to the provided parser. If the '--version' argument already exists, it raises a CommandError.
        
        Parameters:
        parser (ArgumentParser): The argument parser to which the '--version' argument will be added.
        
        Returns:
        None: This function does not return any value. It either adds the '--version' argument or raises a CommandError.
        
        Raises:
        CommandError: If the '--version'
        """

        try:
            parser.add_argument('--version', action='version', version='A.B.C')
        except ArgumentError:
            pass
        else:
            raise CommandError('--version argument does no yet exist')

    def handle(self, *args, **options):
        return 'Detected that --version already exists'
