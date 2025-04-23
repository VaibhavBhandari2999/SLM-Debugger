from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Function to add command-line arguments for a parser.
        
        This function configures a sub-command parser with two levels of sub-commands. The top-level parser is configured to accept a 'subcommand_1' argument. If 'subcommand_1' is set to 'foo_1', a second level of sub-commands is added, with 'subcommand_2' as the argument. If 'subcommand_2' is set to 'foo_2', an argument '--bar' is
        """

        subparsers_1 = parser.add_subparsers(dest='subcommand_1')
        parser_foo_1 = subparsers_1.add_parser('foo_1')
        subparsers_2 = parser_foo_1.add_subparsers(dest='subcommand_2')
        parser_foo_2 = subparsers_2.add_parser('foo_2')
        parser_foo_2.add_argument('--bar', required=True)

    def handle(self, *args, **options):
        self.stdout.write(','.join(options))
