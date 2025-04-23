from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        """
        Function: add_arguments
        
        This function is designed to add command-line arguments to a parser object, specifically for a subcommand named 'foo'. It utilizes subparsers to create a hierarchical structure for command-line arguments.
        
        Parameters:
        - parser: The ArgumentParser object to which the subcommand and its arguments will be added.
        
        Returns:
        - None: This function does not return any value. It modifies the provided parser object in place.
        
        Key Parameters:
        - subparsers: A collection of subparsers created by
        """

        subparsers = parser.add_subparsers()
        parser_foo = subparsers.add_parser('foo')
        parser_foo.add_argument('bar', type=int)

    def handle(self, *args, **options):
        self.stdout.write(','.join(options))
