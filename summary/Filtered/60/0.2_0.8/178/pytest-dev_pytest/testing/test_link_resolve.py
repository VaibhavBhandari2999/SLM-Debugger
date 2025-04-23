import os.path
import subprocess
import sys
import textwrap
from contextlib import contextmanager
from string import ascii_lowercase

import py.path

from _pytest import pytester


@contextmanager
def subst_path_windows(filename):
    """
    Create a temporary file path by substituting a drive letter for a directory path.
    
    This function generates a temporary file path by substituting a drive letter from H-Z for a given directory path. It ensures that the drive letter is not already in use and raises an assertion error if no suitable drive letter is found. The function then creates a temporary file path by combining the drive letter with the base name of the original file path.
    
    Key Parameters:
    - filename (py.path.local): The original file path for
    """

    for c in ascii_lowercase[7:]:  # Create a subst drive from H-Z.
        c += ":"
        if not os.path.exists(c):
            drive = c
            break
    else:
        raise AssertionError("Unable to find suitable drive letter for subst.")

    directory = filename.dirpath()
    basename = filename.basename

    args = ["subst", drive, str(directory)]
    subprocess.check_call(args)
    assert os.path.exists(drive)
    try:
        filename = py.path.local(drive) / basename
        yield filename
    finally:
        args = ["subst", "/D", drive]
        subprocess.check_call(args)


@contextmanager
def subst_path_linux(filename):
    """
    Create a symbolic link to a directory in a parent directory.
    
    This function generates a symbolic link to the given filename in a parent directory named 'sub2'. It yields the new filename with the symbolic link.
    
    Parameters:
    filename (LocalPath): The file or directory to create a symbolic link for.
    
    Yields:
    LocalPath: The new filename with the symbolic link.
    
    Note:
    The original directory is linked to 'sub2' in the parent directory. The symbolic link is created in a
    """

    directory = filename.dirpath()
    basename = filename.basename

    target = directory / ".." / "sub2"
    os.symlink(str(directory), str(target), target_is_directory=True)
    try:
        filename = target / basename
        yield filename
    finally:
        # We don't need to unlink (it's all in the tempdir).
        pass


def test_link_resolve(testdir: pytester.Testdir) -> None:
    """
    See: https://github.com/pytest-dev/pytest/issues/5965
    """
    sub1 = testdir.mkpydir("sub1")
    p = sub1.join("test_foo.py")
    p.write(
        textwrap.dedent(
            """
        import pytest
        def test_foo():
            raise AssertionError()
        """
        )
    )

    subst = subst_path_linux
    if sys.platform == "win32":
        subst = subst_path_windows

    with subst(p) as subst_p:
        result = testdir.runpytest(str(subst_p), "-v")
        # i.e.: Make sure that the error is reported as a relative path, not as a
        # resolved path.
        # See: https://github.com/pytest-dev/pytest/issues/5965
        stdout = result.stdout.str()
        assert "sub1/test_foo.py" not in stdout

        # i.e.: Expect drive on windows because we just have drive:filename, whereas
        # we expect a relative path on Linux.
        expect = (
            "*{}*".format(subst_p) if sys.platform == "win32" else "*sub2/test_foo.py*"
        )
        result.stdout.fnmatch_lines([expect])
