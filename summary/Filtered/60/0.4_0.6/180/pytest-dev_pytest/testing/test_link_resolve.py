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
    Generate a symbolic link to a directory in a parent directory.
    
    This function creates a symbolic link to a directory in a parent directory and yields the new filename. It is designed to work on Linux systems.
    
    Parameters:
    filename (LocalPath): The original filename for which the symbolic link will be created.
    
    Returns:
    LocalPath: The new filename after creating the symbolic link.
    
    Raises:
    OSError: If the symbolic link cannot be created.
    
    Example:
    >>> from pathlib import LocalPath
    >>>
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
([expect])
