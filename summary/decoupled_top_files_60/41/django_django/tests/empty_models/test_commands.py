import io

from django.core.management import call_command
from django.test import TestCase


class CoreCommandsNoOutputTests(TestCase):
    available_apps = ['empty_models']

    def test_sqlflush_no_tables(self):
        """
        Test the sqlflush command when no tables are present.
        
        This function tests the behavior of the 'sqlflush' command when there are no tables in the database. It captures the standard error output and checks if the message 'No tables found.' is printed.
        
        Parameters:
        None
        
        Returns:
        None
        
        Output:
        The function captures the standard error output and asserts that the message 'No tables found.' is printed.
        """

        err = io.StringIO()
        call_command('sqlflush', stderr=err)
        self.assertEqual(err.getvalue(), 'No tables found.\n')

    def test_sqlsequencereset_no_sequences(self):
        """
        Tests the behavior of the 'sqlsequencereset' command when no sequences are found in the specified app.
        
        This function executes the 'sqlsequencereset' command with the 'empty_models' app and captures the standard error output. It then checks if the output indicates that no sequences were found.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Output:
        - The function prints to stderr indicating that no sequences were found.
        
        Example Usage:
        - test_sqlsequencereset_no_sequences()
        """

        err = io.StringIO()
        call_command('sqlsequencereset', 'empty_models', stderr=err)
        self.assertEqual(err.getvalue(), 'No sequences found.\n')
