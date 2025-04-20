from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, **options):
        """
        Handle a command-line operation.
        
        This function processes a command-line operation and outputs a series of messages to the standard output. It writes "Working..." to the console and flushes the buffer to ensure the message is immediately visible. Then, it writes "OK" to confirm the operation's completion.
        
        Parameters:
        **options (dict): Additional keyword arguments that can be used to pass optional parameters to the function.
        
        Returns:
        None: This function does not return any value. It outputs messages to the
        """

        self.stdout.write("Working...")
        self.stdout.flush()
        self.stdout.write("OK")
