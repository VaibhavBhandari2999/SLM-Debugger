from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Function to add command-line arguments for a parser.
        
        This function configures a subparser for a command-line interface, setting up a hierarchical structure of subcommands. The main parser is divided into two levels of subcommands: 'subcommand_1' and 'subcommand_2'. The function adds a subcommand 'foo_1' under the main parser and a subcommand 'foo_2' under 'foo_1'. The 'foo_2' subcommand requires a required argument '--
        """

        subparsers_1 = parser.add_subparsers(dest='subcommand_1')
        parser_foo_1 = subparsers_1.add_parser('foo_1')
        subparsers_2 = parser_foo_1.add_subparsers(dest='subcommand_2')
        parser_foo_2 = subparsers_2.add_parser('foo_2')
        parser_foo_2.add_argument('--bar', required=True)

    def handle(self, *args, **options):
        self.stdout.write(','.join(options))
