from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Function to add command-line arguments for a parser.
        
        This function configures a command-line argument parser to handle subcommands and their respective arguments. It sets up a primary parser with a subcommand group for 'foo_1'. The 'foo_1' subcommand has another subcommand group for 'foo_2', which requires the '--bar' argument.
        
        Parameters:
        parser (argparse.ArgumentParser): The argument parser to configure.
        
        Returns:
        None: This function modifies the provided parser in-place
        """

        subparsers_1 = parser.add_subparsers(dest='subcommand_1')
        parser_foo_1 = subparsers_1.add_parser('foo_1')
        subparsers_2 = parser_foo_1.add_subparsers(dest='subcommand_2')
        parser_foo_2 = subparsers_2.add_parser('foo_2')
        parser_foo_2.add_argument('--bar', required=True)

    def handle(self, *args, **options):
        self.stdout.write(','.join(options))
