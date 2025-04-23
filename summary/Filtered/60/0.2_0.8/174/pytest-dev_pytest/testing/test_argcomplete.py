import subprocess
import sys

import pytest

# test for _argcomplete but not specific for any application


def equal_with_bash(prefix, ffc, fc, out=None):
    """
    Compares the results of a function call with its bash equivalent.
    
    This function takes a prefix string, a Python function (ffc), and a bash function (fc) as input. It calls both functions with the given prefix and compares their results. If an output file is provided, it writes the comparison details to the file. The function returns True if the results are equal, otherwise False.
    
    Parameters:
    prefix (str): The prefix string to be used as input for the functions.
    ffc
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
    try:
        return subprocess.check_output(*args, **kargs).decode().splitlines()
    except subprocess.CalledProcessError:
        return []


class FilesCompleter:
    "File completer class, optionally takes a list of allowed extensions"

    def __init__(self, allowednames=(), directories=True):
        """
        Initialize the object with a list of allowed names and an option to include directories.
        
        Args:
        allowednames (list or str): A list of strings representing the names that are allowed. If a string is provided, it is converted to a list. Each name can optionally start with '*' or '.' which are stripped.
        directories (bool): If True, the object will allow directories in addition to files.
        
        Returns:
        None: This function does not return any value. It initializes the object's attributes
        """

        # Fix if someone passes in a string instead of a list
        if type(allowednames) is str:
            allowednames = [allowednames]

        self.allowednames = [x.lstrip("*").lstrip(".") for x in allowednames]
        self.directories = directories

    def __call__(self, prefix, **kwargs):
        """
        Generate file and directory completions for a given prefix.
        
        This method is designed to be called with a prefix and keyword arguments. It returns a list of completions based on the given prefix and the allowed file types.
        
        Parameters:
        prefix (str): The prefix for which to generate completions.
        allowednames (list, optional): A list of file types to consider for completion. Defaults to None.
        directories (bool, optional): Whether to include directory completions. Defaults to True.
        
        Returns
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
        """this         ls /usr/<TAB>
        """
        from _pytest._argcomplete import FastFilesCompleter

        ffc = FastFilesCompleter()
        fc = FilesCompleter()
        for x in "/usr/".split():
            assert not equal_with_bash(x, ffc, fc, out=sys.stdout)
it():
            assert not equal_with_bash(x, ffc, fc, out=sys.stdout)
