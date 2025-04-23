from django.core.management.base import LabelCommand


class Command(LabelCommand):
    help = "Test Label-based commands"
    requires_system_checks = []

    def handle_label(self, label, **options):
        """
        Executes a label command with the given label and options.
        
        Args:
        label (str): The label of the command to be executed.
        options (dict): Additional keyword arguments to be passed to the command.
        
        This function prints the label and the sorted options to the console.
        """

        print(
            "EXECUTE:LabelCommand label=%s, options=%s"
            % (label, sorted(options.items()))
        )
