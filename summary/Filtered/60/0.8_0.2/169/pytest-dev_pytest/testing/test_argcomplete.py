from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import subprocess
import sys

import pytest

# test for _argcomplete but not specific for any application


def equal_with_bash(prefix, ffc, fc, out=None):
    """
    equal_with_bash(prefix, ffc, fc, out=None)
    
    Compares the results of a function computed in Python (ffc) and a function computed using a bash command (fc) for a given input prefix.
    
    Parameters:
    prefix (str): The input string or identifier for which the functions will be evaluated.
    ffc (function): A Python function that takes a prefix and returns a set of results.
    fc (function): A bash command function that takes a prefix and returns
    """

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
    Wraps a system call to execute a subprocess and return its output.
    
    This function is designed to execute a system command and capture its output. It supports both Python 2 and 3, ensuring compatibility across different versions. The function can handle both positional and keyword arguments, and it can decode the output from bytes to a string.
    
    Parameters:
    *args: Positional arguments to be passed to `subprocess.Popen`.
    **kargs: Keyword arguments to be passed to `subprocess.Popen`.
    """

    try:
        if sys.version_info > (2, 7):
            return subprocess.check_output(*args, **kargs).decode().splitlines()
        if "stdout" in kargs:
            raise ValueError("stdout argument not allowed, it will be overridden.")
        process = subprocess.Popen(stdout=subprocess.PIPE, *args, **kargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kargs.get("args")
            if cmd is None:
                cmd = args[0]
            raise subprocess.CalledProcessError(retcode, cmd)
        return output.decode().splitlines()
    except subprocess.CalledProcessError:
        return []


class FilesCompleter(object):
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


class TestArgComplete(object):
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
_bash(x, ffc, fc, out=sys.stdout)
