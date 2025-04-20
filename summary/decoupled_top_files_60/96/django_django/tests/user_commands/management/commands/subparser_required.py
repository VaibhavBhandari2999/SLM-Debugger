from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Function to add arguments to a command-line parser.
        
        This function configures a command-line parser to handle subcommands and their respective arguments. It sets up a main parser with a subcommand for 'foo_1', which in turn has a subcommand for 'foo_2'. The 'foo_2' subcommand requires a required argument '--bar'.
        
        Parameters:
        parser (argparse.ArgumentParser): The command-line argument parser to be configured.
        
        Returns:
        None: This function does not return any
        """

        subparsers_1 = parser.add_subparsers(dest="subcommand_1")
        parser_foo_1 = subparsers_1.add_parser("foo_1")
        subparsers_2 = parser_foo_1.add_subparsers(dest="subcommand_2")
        parser_foo_2 = subparsers_2.add_parser("foo_2")
        parser_foo_2.add_argument("--bar", required=True)

    def handle(self, *args, **options):
        self.stdout.write(",".join(options))
