from argparse import ArgumentError

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Function: add_arguments
        
        This function adds command-line arguments to a parser object.
        
        Parameters:
        - parser: The argument parser object to which the arguments will be added.
        
        Key Points:
        - Attempts to add a '--version' argument with a version number 'A.B.C'.
        - If the '--version' argument already exists, it catches the ArgumentError and does nothing.
        - If the '--version' argument does not exist and adding it fails, it raises a CommandError indicating that the '--version' argument does
        """

        try:
            parser.add_argument('--version', action='version', version='A.B.C')
        except ArgumentError:
            pass
        else:
            raise CommandError('--version argument does no yet exist')

    def handle(self, *args, **options):
        return 'Detected that --version already exists'
