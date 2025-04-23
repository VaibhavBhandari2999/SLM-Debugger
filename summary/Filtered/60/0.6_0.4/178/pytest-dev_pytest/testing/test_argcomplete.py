import subprocess
import sys

import pytest

# test for _argcomplete but not specific for any application


def equal_with_bash(prefix, ffc, fc, out=None):
    res = ffc(prefix)
    res_bash = set(fc(prefix))
    retval = set(res) == res_bash
    if out:
        out.write("equal_with_bash({}) {} {}\n".format(prefix, retval, res))
        if not retval:
            out.write(" python - bash: %s\n" % (set(res) - res_bash))
            out.write(" bash - python: %s\n" % (res_bash - set(res)))
    return retval


# copied from argcomplete.completers as import from there
# also pulls in argcomplete.__init__ which opens filedescriptor 9
# this gives an OSError at the end of testrun


def _wrapcall(*args, **kargs):
    """
    Wraps a call to subprocess.check_output to execute a command and return its output as a list of lines. If the command fails, an empty list is returned.
    
    Parameters:
    *args: Variable length argument list to be passed to subprocess.check_output.
    **kargs: Arbitrary keyword arguments to be passed to subprocess.check_output.
    
    Returns:
    A list of strings, each representing a line of the command's output. If the command fails, an empty list is returned.
    """

    try:
        return subprocess.check_output(*args, **kargs).decode().splitlines()
    except subprocess.CalledProcessError:
        return []


class FilesCompleter:
    "File completer class, optionally takes a list of allowed extensions"

    def __init__(self, allowednames=(), directories=True):
        # Fix if someone passes in a string instead of a list
        if type(allowednames) is str:
            allowednames = [allowednames]

        self.allowednames = [x.lstrip("*").lstrip(".") for x in allowednames]
        self.directories = directories

    def __call__(self, prefix, **kwargs):
        completion = []
        if self.allowednames:
            if self.directories:
                files = _wrapcall(
                    ["bash", "-c", "compgen -A directory -- '{p}'".format(p=prefix)]
                )
                completion += [f + "/" for f in files]
            for x in self.allowednames:
                completion += _wrapcall(
                    [
                        "bash",
                        "-c",
                        "compgen -A file -X '!*.{0}' -- '{p}'".format(x, p=prefix),
                    ]
                )
        else:
            completion += _wrapcall(
                ["bash", "-c", "compgen -A file -- '{p}'".format(p=prefix)]
            )

            anticomp = _wrapcall(
                ["bash", "-c", "compgen -A directory -- '{p}'".format(p=prefix)]
            )

            completion = list(set(completion) - set(anticomp))

            if self.directories:
                completion += [f + "/" for f in anticomp]
        return completion


class TestArgComplete:
    @pytest.mark.skipif("sys.platform in ('win32', 'darwin')")
    def test_compare_with_compgen(self, tmpdir):
        """
        Tests the `FastFilesCompleter` and `FilesCompleter` classes by comparing their behavior with the `compgen` command in bash.
        
        This function checks the output of the `FastFilesCompleter` and `FilesCompleter` classes for various input strings. It ensures that the completions provided by these classes match the expected completions from the `compgen` command in a bash shell.
        
        Parameters:
        - tmpdir (py.path.local): A temporary directory used for testing.
        """

        from _pytest._argcomplete import FastFilesCompleter

        ffc = FastFilesCompleter()
        fc = FilesCompleter()

        with tmpdir.as_cwd():
            assert equal_with_bash("", ffc, fc, out=sys.stdout)

            tmpdir.ensure("data")

            for x in ["d", "data", "doesnotexist", ""]:
                assert equal_with_bash(x, ffc, fc, out=sys.stdout)

    @pytest.mark.skipif("sys.platform in ('win32', 'darwin')")
    def test_remove_dir_prefix(self):
        """this is not compatible with compgen but it is with bash itself:
        ls /usr/<TAB>
        """
        from _pytest._argcomplete import FastFilesCompleter

        ffc = FastFilesCompleter()
        fc = FilesCompleter()
        for x in "/usr/".split():
            assert not equal_with_bash(x, ffc, fc, out=sys.stdout)
