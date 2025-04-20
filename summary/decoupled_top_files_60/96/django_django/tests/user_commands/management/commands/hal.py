from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Useless command."

    def add_arguments(self, parser):
        """
        Add command-line arguments to the parser.
        
        This method adds arguments to the argument parser for a command-line interface.
        
        Args:
        parser (argparse.ArgumentParser): The argument parser to which the arguments will be added.
        
        Key Arguments:
        - `args` (list of str): The app labels to work on. Can be specified as zero or more arguments.
        - `--empty` (bool): A flag indicating whether to perform any action. If set to `True`, the command will not perform
        """

        parser.add_argument(
            "args",
            metavar="app_label",
            nargs="*",
            help="Specify the app label(s) to works on.",
        )
        parser.add_argument("--empty", action="store_true", help="Do nothing.")

    def handle(self, *app_labels, **options):
        app_labels = set(app_labels)

        if options["empty"]:
            self.stdout.write()
            self.stdout.write("Dave, I can't do that.")
            return

        if not app_labels:
            raise CommandError("I'm sorry Dave, I'm afraid I can't do that.")

        # raise an error if some --parameter is flowing from options to args
        for app_label in app_labels:
            if app_label.startswith("--"):
                raise CommandError("Sorry, Dave, I can't let you do that.")

        self.stdout.write("Dave, my mind is going. I can feel it. I can feel it.")
