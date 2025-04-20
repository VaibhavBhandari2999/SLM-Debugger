from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Test basic commands"
    requires_system_checks = []

    def add_arguments(self, parser):
        """
        Add command-line arguments to the parser.
        
        This function configures the argument parser for the command-line interface.
        
        Args:
        parser (argparse.ArgumentParser): The argument parser to which the arguments will be added.
        
        Key Arguments:
        - `args` (list, optional): A list of positional arguments. Defaults to an empty list.
        - `--option_a` (str, optional): A positional or keyword argument with a default value of '1'. Defaults to '1'.
        - `--
        """

        parser.add_argument("args", nargs="*")
        parser.add_argument("--option_a", "-a", default="1")
        parser.add_argument("--option_b", "-b", default="2")
        parser.add_argument("--option_c", "-c", default="3")

    def handle(self, *labels, **options):
        """
        Handle command execution with specified labels and options.
        
        This method is designed to execute a command with given labels and options.
        
        Parameters:
        *labels (tuple): Variable length argument list of labels for the command.
        **options (dict): Arbitrary keyword arguments representing command options.
        
        Output:
        None: This method prints the command details to the console and does not return any value.
        """

        print(
            "EXECUTE:BaseCommand labels=%s, options=%s"
            % (labels, sorted(options.items()))
        )
