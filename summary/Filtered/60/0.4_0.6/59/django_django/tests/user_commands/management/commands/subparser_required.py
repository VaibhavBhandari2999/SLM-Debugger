from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Function to add command-line arguments for a parser.
        
        This function configures a subcommand parser with two levels of subcommands. The main parser is configured to accept a 'subcommand_1' argument, which determines the specific subcommand to be executed. The 'foo_1' subcommand is further divided into a 'foo_2' subcommand, which requires a '--bar' argument.
        
        Parameters:
        parser (argparse.ArgumentParser): The main argument parser to which the subcommands will be
        """

        subparsers_1 = parser.add_subparsers(dest='subcommand_1')
        parser_foo_1 = subparsers_1.add_parser('foo_1')
        subparsers_2 = parser_foo_1.add_subparsers(dest='subcommand_2')
        parser_foo_2 = subparsers_2.add_parser('foo_2')
        parser_foo_2.add_argument('--bar', required=True)

    def handle(self, *args, **options):
        self.stdout.write(','.join(options))
