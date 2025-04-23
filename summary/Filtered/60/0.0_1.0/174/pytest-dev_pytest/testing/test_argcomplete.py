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
# this gives an IOError at the end of testrun


def _wrapcall(*args, **kargs):
    """
    Wraps a system call using subprocess.check_output.
    
    This function attempts to execute a system command and capture its output. The command and its arguments are passed as a tuple to the function. The function returns a list of lines from the command's output. If the command fails, an empty list is returned.
    
    Parameters:
    *args: A tuple containing the command and its arguments.
    **kargs: Additional keyword arguments to pass to subprocess.check_output.
    
    Returns:
    A list of strings,
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
        """
        Generate file and directory completions based on the given prefix.
        
        This function is designed to be called with a prefix and additional keyword arguments. It returns a list of possible completions for files and directories that match the given prefix.
        
        Parameters:
        prefix (str): The prefix to match against file and directory names.
        kwargs (dict): Additional keyword arguments (not used in this function).
        
        Returns:
        list: A list of strings representing possible completions for files and directories.
        """

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
