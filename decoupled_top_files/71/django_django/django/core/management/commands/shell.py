"""
```markdown
This Django management command runs a Python interactive interpreter. It tries to use IPython or bpython if available, falling back to Python itself. The command accepts various options to customize the behavior, such as specifying an interface, ignoring startup scripts, or running a specific command. It also provides tab completion and handles standard input execution.
```

### Detailed Docstring:
```python
"""
import os
import select
import sys
import traceback

from django.core.management import BaseCommand, CommandError
from django.utils.datastructures import OrderedSet


class Command(BaseCommand):
    help = (
        "Runs a Python interactive interpreter. Tries to use IPython or "
        "bpython, if one of them is available. Any standard input is executed "
        "as code."
    )

    requires_system_checks = []
    shells = ['ipython', 'bpython', 'python']

    def add_arguments(self, parser):
        """
        Add command-line arguments to the parser.
        
        Args:
        parser (argparse.ArgumentParser): The argument parser to which the arguments will be added.
        
        Adds the following arguments:
        - `--no-startup`: When using plain Python, ignore the PYTHONSTARTUP environment variable and ~/.pythonrc.py script.
        - `-i`, `--interface`: Specify an interactive interpreter interface. Available options: "ipython", "bpython", and "python".
        - `-c`, `--command
        """

        parser.add_argument(
            '--no-startup', action='store_true',
            help='When using plain Python, ignore the PYTHONSTARTUP environment variable and ~/.pythonrc.py script.',
        )
        parser.add_argument(
            '-i', '--interface', choices=self.shells,
            help='Specify an interactive interpreter interface. Available options: "ipython", "bpython", and "python"',
        )
        parser.add_argument(
            '-c', '--command',
            help='Instead of opening an interactive shell, run a command as Django and exit.',
        )

    def ipython(self, options):
        from IPython import start_ipython
        start_ipython(argv=[])

    def bpython(self, options):
        import bpython
        bpython.embed()

    def python(self, options):
        """
        This function sets up a Python interactive shell environment for the user. It imports the `code` module and initializes a dictionary named `imported_objects` to store imported objects for tab completion. If the `readline` module is available, it configures tab completion. The function then checks for the presence of `$PYTHONSTARTUP` or `.pythonrc.py` files and executes their contents if they exist. Finally, it starts an interactive Python shell using the `code.interact()` method with the
        """

        import code

        # Set up a dictionary to serve as the environment for the shell, so
        # that tab completion works on objects that are imported at runtime.
        imported_objects = {}
        try:  # Try activating rlcompleter, because it's handy.
            import readline
        except ImportError:
            pass
        else:
            # We don't have to wrap the following import in a 'try', because
            # we already know 'readline' was imported successfully.
            import rlcompleter
            readline.set_completer(rlcompleter.Completer(imported_objects).complete)
            # Enable tab completion on systems using libedit (e.g. macOS).
            # These lines are copied from Python's Lib/site.py.
            readline_doc = getattr(readline, '__doc__', '')
            if readline_doc is not None and 'libedit' in readline_doc:
                readline.parse_and_bind("bind ^I rl_complete")
            else:
                readline.parse_and_bind("tab:complete")

        # We want to honor both $PYTHONSTARTUP and .pythonrc.py, so follow system
        # conventions and get $PYTHONSTARTUP first then .pythonrc.py.
        if not options['no_startup']:
            for pythonrc in OrderedSet([os.environ.get("PYTHONSTARTUP"), os.path.expanduser('~/.pythonrc.py')]):
                if not pythonrc:
                    continue
                if not os.path.isfile(pythonrc):
                    continue
                with open(pythonrc) as handle:
                    pythonrc_code = handle.read()
                # Match the behavior of the cpython shell where an error in
                # PYTHONSTARTUP prints an exception and continues.
                try:
                    exec(compile(pythonrc_code, pythonrc, 'exec'), imported_objects)
                except Exception:
                    traceback.print_exc()

        code.interact(local=imported_objects)

    def handle(self, **options):
        """
        This function handles the execution of commands or stdin input based on the provided options. It supports multiple interfaces and executes the specified command or reads from stdin if available. If no specific command is provided, it attempts to execute the default interface.
        
        :param options: A dictionary containing the following keys:
        - 'command': The command to be executed.
        - 'interface': The interface to use for execution.
        :type options: dict
        
        :raises CommandError: If the specified interface cannot
        """

        # Execute the command and exit.
        if options['command']:
            exec(options['command'], globals())
            return

        # Execute stdin if it has anything to read and exit.
        # Not supported on Windows due to select.select() limitations.
        if sys.platform != 'win32' and not sys.stdin.isatty() and select.select([sys.stdin], [], [], 0)[0]:
            exec(sys.stdin.read(), globals())
            return

        available_shells = [options['interface']] if options['interface'] else self.shells

        for shell in available_shells:
            try:
                return getattr(self, shell)(options)
            except ImportError:
                pass
        raise CommandError("Couldn't import {} interface.".format(shell))
