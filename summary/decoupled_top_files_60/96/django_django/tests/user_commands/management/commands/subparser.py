from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Function: add_arguments
        
        Summary:
        This function is designed to add command-line arguments to a parser object using the argparse module. It creates sub-commands and adds specific arguments to them.
        
        Parameters:
        - parser: An instance of the argparse.ArgumentParser class.
        
        Returns:
        - None: This function does not return any value. It modifies the provided parser object in-place.
        
        Description:
        The function `add_arguments` is used to configure an argument parser for a command-line interface. It sets up a sub-command
        """

        subparsers = parser.add_subparsers()
        parser_foo = subparsers.add_parser("foo")
        parser_foo.add_argument("bar", type=int)

    def handle(self, *args, **options):
        self.stdout.write(",".join(options))
