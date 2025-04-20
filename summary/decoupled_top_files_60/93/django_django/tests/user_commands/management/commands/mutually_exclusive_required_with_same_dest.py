from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Adds command-line arguments to the parser.
        
        This method sets up a mutually exclusive group of arguments that are required for the parser. The group includes two options: "--for" and "--until". These arguments are used to specify a time range for the operation.
        
        Parameters:
        parser (argparse.ArgumentParser): The argument parser to which the arguments will be added.
        
        Key Arguments:
        - `group`: A mutually exclusive group of arguments.
        - `dest="until"`: The destination for the "--for
        """

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--for", dest="until", action="store")
        group.add_argument("--until", action="store")

    def handle(self, *args, **options):
        for option, value in options.items():
            if value is not None:
                self.stdout.write("%s=%s" % (option, value))
