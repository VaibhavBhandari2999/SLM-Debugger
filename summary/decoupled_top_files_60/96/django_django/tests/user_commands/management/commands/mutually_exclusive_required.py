from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Add command-line arguments for a function.
        
        This function adds mutually exclusive arguments to the argument parser. The user must provide exactly one of the following arguments:
        - `--foo-id` (int): An integer ID for the foo.
        - `--foo-name` (str): A string name for the foo.
        - `--foo-list` (list of int): A list of integer IDs for the foo.
        - `--append_const` (list): Appends the value 42 to the
        """

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--foo-id", type=int, nargs="?", default=None)
        group.add_argument("--foo-name", type=str, nargs="?", default=None)
        group.add_argument("--foo-list", type=int, nargs="+")
        group.add_argument("--append_const", action="append_const", const=42)
        group.add_argument("--const", action="store_const", const=31)
        group.add_argument("--count", action="count")
        group.add_argument("--flag_false", action="store_false")
        group.add_argument("--flag_true", action="store_true")

    def handle(self, *args, **options):
        for option, value in options.items():
            if value is not None:
                self.stdout.write("%s=%s" % (option, value))
alue in options.items():
            if value is not None:
                self.stdout.write("%s=%s" % (option, value))
