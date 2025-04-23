from django.core.management.base import LabelCommand


class Command(LabelCommand):
    help = "Test Label-based commands"
    requires_system_checks = []

    def handle_label(self, label, **options):
        """
        Handle a label command.
        
        Args:
        label (str): The label to be processed.
        **options (dict): Additional keyword arguments to be passed to the command.
        
        This function prints a formatted string detailing the label and the options passed to it.
        """

        print(
            "EXECUTE:LabelCommand label=%s, options=%s"
            % (label, sorted(options.items()))
        )
