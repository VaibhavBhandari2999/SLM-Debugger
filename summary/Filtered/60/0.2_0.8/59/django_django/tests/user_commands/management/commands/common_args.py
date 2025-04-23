from argparse import ArgumentError

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Function to add command-line arguments to a parser.
        
        This function attempts to add a '--version' argument to the provided parser. If the '--version' argument already exists, it will raise a CommandError. The function handles the case where the ArgumentError is raised, indicating that the '--version' argument is not yet available.
        
        Parameters:
        parser (argparse.ArgumentParser): The argument parser to which the '--version' argument will be added.
        
        Returns:
        None: This function does not return any value.
        """

        try:
            parser.add_argument('--version', action='version', version='A.B.C')
        except ArgumentError:
            pass
        else:
            raise CommandError('--version argument does no yet exist')

    def handle(self, *args, **options):
        return 'Detected that --version already exists'
