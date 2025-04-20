import sys
import unittest
from unittest import mock

from django import __version__
from django.core.management import CommandError, call_command
from django.test import SimpleTestCase
from django.test.utils import captured_stdin, captured_stdout


class ShellCommandTestCase(SimpleTestCase):

    def test_command_option(self):
        """
        Tests the command option functionality.
        
        This function tests the command option by executing a Django shell command that imports the django module, retrieves the logger for the 'test' module, and logs the Django version using the INFO level. The test logs the Django version and asserts that the log message matches the expected version.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the log message does not match the expected Django version.
        
        Usage:
        This function is typically used in a Django test
        """

        with self.assertLogs('test', 'INFO') as cm:
            call_command(
                'shell',
                command=(
                    'import django; from logging import getLogger; '
                    'getLogger("test").info(django.__version__)'
                ),
            )
        self.assertEqual(cm.records[0].getMessage(), __version__)

    @unittest.skipIf(sys.platform == 'win32', "Windows select() doesn't support file descriptors.")
    @mock.patch('django.core.management.commands.shell.select')
    def test_stdin_read(self, select):
        with captured_stdin() as stdin, captured_stdout() as stdout:
            stdin.write('print(100)\n')
            stdin.seek(0)
            call_command('shell')
        self.assertEqual(stdout.getvalue().strip(), '100')

    @mock.patch('django.core.management.commands.shell.select.select')  # [1]
    @mock.patch.dict('sys.modules', {'IPython': None})
    def test_shell_with_ipython_not_installed(self, select):
        """
        Tests the behavior of the 'shell' command when the 'ipython' interface is requested but not installed.
        
        This function simulates the 'shell' command call with the 'ipython' interface option and checks if a CommandError is raised when the ipython package is not installed.
        
        Parameters:
        select (unittest.mock.Mock): A mock object representing the select function used to simulate the result of the shell command call.
        
        Returns:
        None: The function asserts that a CommandError is raised with the
        """

        select.return_value = ([], [], [])
        with self.assertRaisesMessage(CommandError, "Couldn't import ipython interface."):
            call_command('shell', interface='ipython')

    @mock.patch('django.core.management.commands.shell.select.select')  # [1]
    @mock.patch.dict('sys.modules', {'bpython': None})
    def test_shell_with_bpython_not_installed(self, select):
        select.return_value = ([], [], [])
        with self.assertRaisesMessage(CommandError, "Couldn't import bpython interface."):
            call_command('shell', interface='bpython')

    # [1] Patch select to prevent tests failing when when the test suite is run
    # in parallel mode. The tests are run in a subprocess and the subprocess's
    # stdin is closed and replaced by /dev/null. Reading from /dev/null always
    # returns EOF and so select always shows that sys.stdin is ready to read.
    # This causes problems because of the call to select.select() towards the
    # end of shell's handle() method.
 method.
