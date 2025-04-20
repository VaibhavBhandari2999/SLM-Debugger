from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Adds command-line arguments to the parser.
        
        This method configures the argument parser to accept either the `--for` or `--until` argument, which are mutually exclusive. Exactly one of these arguments must be provided. The `--for` argument is an alias for `--until`.
        
        Parameters:
        parser (argparse.ArgumentParser): The argument parser to which the arguments will be added.
        
        Returns:
        None: This method does not return any value. It modifies the provided `parser` object in
        """

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--for", dest="until", action="store")
        group.add_argument("--until", action="store")

    def handle(self, *args, **options):
        for option, value in options.items():
            if value is not None:
                self.stdout.write("%s=%s" % (option, value))
