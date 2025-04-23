from argparse import ArgumentError

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Function: add_arguments
        
        This function adds command-line arguments to a parser object.
        
        Parameters:
        - parser: The ArgumentParser object to which the argument will be added.
        
        Key Points:
        - The function attempts to add a --version argument with a specified version number.
        - If the --version argument already exists, the function catches the ArgumentError and proceeds.
        - If the --version argument does not yet exist, the function raises a CommandError.
        
        Returns:
        - None: The function modifies the parser object in place
        """

        try:
            parser.add_argument('--version', action='version', version='A.B.C')
        except ArgumentError:
            pass
        else:
            raise CommandError('--version argument does no yet exist')

    def handle(self, *args, **options):
        return 'Detected that --version already exists'
