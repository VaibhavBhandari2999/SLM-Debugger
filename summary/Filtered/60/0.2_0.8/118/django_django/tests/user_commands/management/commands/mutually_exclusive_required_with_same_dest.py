from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Adds command-line arguments to the parser.
        
        This method configures the parser to accept either the `--for` or `--until` argument, which are mutually exclusive. Exactly one of these arguments must be provided.
        
        Args:
        parser (argparse.ArgumentParser): The argument parser to which the arguments will be added.
        
        Key Arguments:
        - `--for` (alias `--until`): A required argument that specifies the start date or time for a certain operation.
        - `--until`:
        """

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--for", dest="until", action="store")
        group.add_argument("--until", action="store")

    def handle(self, *args, **options):
        """
        This function processes command-line options passed to a Django management command. It iterates through the provided options and writes each option and its corresponding value to the standard output if the value is not None. The function does not return any value.
        
        Parameters:
        *args: Variable length argument list. Not used in this function.
        **options: Arbitrary keyword arguments representing command-line options.
        
        Returns:
        None. The function writes the option-value pairs to the standard output.
        
        Example Usage:
        handle(None,
        """

        for option, value in options.items():
            if value is not None:
                self.stdout.write("%s=%s" % (option, value))
