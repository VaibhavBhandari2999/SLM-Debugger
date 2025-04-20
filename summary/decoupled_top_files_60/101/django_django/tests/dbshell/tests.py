from unittest import mock

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.test import SimpleTestCase


class DbshellCommandTestCase(SimpleTestCase):
    def test_command_missing(self):
        """
        Tests the behavior of the `dbshell` command when the required executable is missing.
        
        This function checks if the `dbshell` command raises a `CommandError` when the required executable is not found or not in the system path. The key parameters are:
        - `self`: The test case instance.
        
        The function does not return any value but raises a `CommandError` with a specific message if the executable is missing.
        
        Key points:
        - The function uses a mock patch to simulate the absence of
        """

        msg = (
            "You appear not to have the %r program installed or on your path."
            % connection.client.executable_name
        )
        with self.assertRaisesMessage(CommandError, msg):
            with mock.patch("subprocess.run", side_effect=FileNotFoundError):
                call_command("dbshell")
