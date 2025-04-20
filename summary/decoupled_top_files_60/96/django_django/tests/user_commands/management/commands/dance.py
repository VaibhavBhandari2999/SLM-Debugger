from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Dance around like a madman."
    args = ""
    requires_system_checks = "__all__"

    def add_arguments(self, parser):
        """
        Summary:
        This function adds command-line arguments to a parser object for a command-line interface (CLI) tool. The function is typically used in a larger CLI application to define the expected input parameters and options.
        
        Parameters:
        - parser: The ArgumentParser object from the argparse module to which the arguments will be added.
        
        Key Arguments:
        - `integer`: An optional integer argument that defaults to 0 if not provided. It can be specified as a positional argument.
        - `style`: A required string argument
        """

        parser.add_argument("integer", nargs="?", type=int, default=0)
        parser.add_argument("-s", "--style", default="Rock'n'Roll")
        parser.add_argument("-x", "--example")
        parser.add_argument("--opt-3", action="store_true", dest="option3")

    def handle(self, *args, **options):
        """
        Handle command execution.
        
        This function processes command options and performs actions based on the provided arguments. It can raise a CommandError with a specified return code if the 'example' option is set to 'raise'. It also writes messages to the standard output based on the verbosity level and other options.
        
        Parameters:
        *args: Variable length argument list (not used in this function).
        **options: Arbitrary keyword arguments representing command options:
        - example (str): If set to 'raise', a Command
        """

        example = options["example"]
        if example == "raise":
            raise CommandError(returncode=3)
        if options["verbosity"] > 0:
            self.stdout.write("I don't feel like dancing %s." % options["style"])
            self.stdout.write(",".join(options))
        if options["integer"] > 0:
            self.stdout.write(
                "You passed %d as a positional argument." % options["integer"]
            )
