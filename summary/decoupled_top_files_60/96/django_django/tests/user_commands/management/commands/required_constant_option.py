from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Adds command-line arguments to the parser.
        
        This function configures the argument parser with several required arguments:
        - `--append_const`: Appends the value 42 to the argument list each time it is provided.
        - `--const`: Sets the argument to the value 31.
        - `--count`: Counts the number of times the argument is provided.
        - `--flag_false`: Sets the argument to False if provided.
        - `--flag_true`: Sets the argument to True if provided
        """

        parser.add_argument(
            "--append_const",
            action="append_const",
            const=42,
            required=True,
        )
        parser.add_argument("--const", action="store_const", const=31, required=True)
        parser.add_argument("--count", action="count", required=True)
        parser.add_argument("--flag_false", action="store_false", required=True)
        parser.add_argument("--flag_true", action="store_true", required=True)

    def handle(self, *args, **options):
        """
        The handle function processes command-line options and outputs them to the console. It takes in variable arguments (*args) and keyword arguments (**options). The function iterates over the keyword arguments, checking if the value is not None. If the value is not None, it writes the option and its corresponding value to the standard output. This function is typically used in Django management commands to handle and display command-line options.
        
        Parameters:
        *args: Variable positional arguments (not used in this function).
        **
        """

        for option, value in options.items():
            if value is not None:
                self.stdout.write("%s=%s" % (option, value))
