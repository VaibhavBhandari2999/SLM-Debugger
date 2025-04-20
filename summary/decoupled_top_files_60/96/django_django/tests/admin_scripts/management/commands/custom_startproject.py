from django.core.management.commands.startproject import Command as BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Adds command-line arguments to the parser.
        
        This method extends the functionality of the base class by adding an additional argument to the parser. The argument `--extra` is an optional parameter that allows users to pass an arbitrary extra value to the context.
        
        Args:
        parser (argparse.ArgumentParser): The argument parser to which the new argument will be added.
        
        Returns:
        None: This method does not return any value. It modifies the provided parser in place.
        """

        super().add_arguments(parser)
        parser.add_argument(
            "--extra", help="An arbitrary extra value passed to the context"
        )
