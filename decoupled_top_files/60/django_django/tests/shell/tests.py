"""
```markdown
This Python file contains unit tests for the Django shell command. It defines a single test case class `ShellCommandTestCase` that includes four test methods:

1. `test_command_option`: Verifies that the Django shell command correctly logs the Django version.
2. `test_stdin_read`: Ensures that the shell command can read and execute Python expressions provided via standard input.
3. `test_shell_with_ipython_not_installed`: Checks that the shell command fails gracefully if the IPython interface is requested but not available.
4. `test_shell_with_bpython_not_installed`: Verifies that the shell command fails appropriately if the bpython interface is requested but not available.

The tests utilize Django's `call_command` function to execute the
"""
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
        Tests the behavior of the 'shell' command option, which executes a Django shell command and logs the version of Django using the 'getLogger' function from the 'logging' module. The test asserts that the log message contains the expected Django version.
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
        """
        Tests the `stdin_read` functionality of the shell command.
        
        This test captures the standard input and output, writes a Python expression to the input,
        seeks to the beginning of the input buffer, and calls the `shell` command. It then asserts
        that the output matches the expected result.
        
        - **Functions Used**: `captured_stdin`, `captured_stdout`, `call_command`
        - **Input**: Python expression written to standard input
        - **Output**: Result
        """

        with captured_stdin() as stdin, captured_stdout() as stdout:
            stdin.write('print(100)\n')
            stdin.seek(0)
            call_command('shell')
        self.assertEqual(stdout.getvalue().strip(), '100')

    @mock.patch('django.core.management.commands.shell.select.select')  # [1]
    @mock.patch.dict('sys.modules', {'IPython': None})
    def test_shell_with_ipython_not_installed(self, select):
        """
        Test the shell command with IPython not installed.
        
        This test checks that the shell command raises a CommandError when
        attempting to use the IPython interface without having IPython
        installed. The `call_command` function is used to simulate the
        execution of the 'shell' command with the specified interface.
        
        Args:
        select (unittest.mock.Mock): A mock object representing the select
        function used to simulate the return values.
        
        Raises:
        CommandError: If the
        """

        select.return_value = ([], [], [])
        with self.assertRaisesMessage(CommandError, "Couldn't import ipython interface."):
            call_command('shell', interface='ipython')

    @mock.patch('django.core.management.commands.shell.select.select')  # [1]
    @mock.patch.dict('sys.modules', {'bpython': None})
    def test_shell_with_bpython_not_installed(self, select):
        """
        Tests the behavior of the shell command when the bpython interface is requested but not installed.
        
        :param select: A mock object representing the select module.
        :raises CommandError: If bpython is not installed and the shell command is called with the 'bpython' interface.
        """

        select.return_value = ([], [], [])
        with self.assertRaisesMessage(CommandError, "Couldn't import bpython interface."):
            call_command('shell', interface='bpython')

    # [1] Patch select to prevent tests failing when when the test suite is run
    # in parallel mode. The tests are run in a subprocess and the subprocess's
    # stdin is closed and replaced by /dev/null. Reading from /dev/null always
    # returns EOF and so select always shows that sys.stdin is ready to read.
    # This causes problems because of the call to select.select() towards the
    # end of shell's handle() method.
