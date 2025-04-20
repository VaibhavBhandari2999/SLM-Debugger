from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Add command-line arguments to the parser.
        
        This method adds a mutually exclusive group of arguments to the parser. The group is required and contains two options:
        - `--for`: A positional argument that stores the value in the `until` attribute of the destination.
        - `--until`: A positional argument that stores the value directly.
        
        Parameters:
        parser (argparse.ArgumentParser): The argument parser to which the arguments will be added.
        
        Returns:
        None: This method does not return any value. It
        """

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--for", dest="until", action="store")
        group.add_argument("--until", action="store")

    def handle(self, *args, **options):
        """
        This function processes command-line options and outputs them to the standard output. It iterates over the options dictionary, checking if the value is not None. If the value is not None, it writes the option and its corresponding value to the standard output.
        
        Parameters:
        *args: Variable length argument list (not used in this function).
        **options: Arbitrary keyword arguments representing command-line options.
        
        Returns:
        None: This function does not return any value. It outputs the options to the standard output
        """

        for option, value in options.items():
            if value is not None:
                self.stdout.write("%s=%s" % (option, value))
