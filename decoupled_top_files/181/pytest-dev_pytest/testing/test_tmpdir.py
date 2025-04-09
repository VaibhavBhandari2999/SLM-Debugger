import os
import stat
import sys
from pathlib import Path
from typing import Callable
from typing import cast
from typing import List

import attr

import pytest
from _pytest import pathlib
from _pytest.config import Config
from _pytest.pathlib import cleanup_numbered_dir
from _pytest.pathlib import create_cleanup_lock
from _pytest.pathlib import make_numbered_dir
from _pytest.pathlib import maybe_delete_a_numbered_dir
from _pytest.pathlib import on_rm_rf_error
from _pytest.pathlib import register_cleanup_lock_removal
from _pytest.pathlib import rm_rf
from _pytest.pytester import Pytester
from _pytest.tmpdir import get_user
from _pytest.tmpdir import TempdirFactory
from _pytest.tmpdir import TempPathFactory


def test_tmpdir_fixture(pytester: Pytester) -> None:
    """
    Test the functionality of the tmpdir fixture.
    
    This test verifies that the `tmpdir` fixture is correctly utilized in the
    example file "tmpdir/tmpdir_fixture.py". The `tmpdir` fixture creates a
    temporary directory that can be used for testing purposes, ensuring that
    no data persists between tests.
    
    Args:
    pytester (Pytester): A fixture provided by the `pytester` package,
    which allows for running and asserting on pytest sessions.
    """

    p = pytester.copy_example("tmpdir/tmpdir_fixture.py")
    results = pytester.runpytest(p)
    results.stdout.fnmatch_lines(["*1 passed*"])


@attr.s
class FakeConfig:
    basetemp = attr.ib()

    @property
    def trace(self):
        return self

    def get(self, key):
        return lambda *k: None

    @property
    def option(self):
        return self


class TestTempdirHandler:
    def test_mktemp(self, tmp_path):
        """
        Generates temporary files or directories using the `TempdirFactory` class from the given configuration.
        
        Args:
        self: The instance of the class containing the method.
        tmp_path (pathlib.Path): A temporary directory path.
        
        Returns:
        None
        
        Summary:
        This function creates temporary files or directories using the `TempdirFactory` class based on the provided configuration. It uses the `mktemp` method to generate unique temporary paths and checks if they are relative to the base
        """

        config = cast(Config, FakeConfig(tmp_path))
        t = TempdirFactory(
            TempPathFactory.from_config(config, _ispytest=True), _ispytest=True
        )
        tmp = t.mktemp("world")
        assert tmp.relto(t.getbasetemp()) == "world0"
        tmp = t.mktemp("this")
        assert tmp.relto(t.getbasetemp()).startswith("this")
        tmp2 = t.mktemp("this")
        assert tmp2.relto(t.getbasetemp()).startswith("this")
        assert tmp2 != tmp

    def test_tmppath_relative_basetemp_absolute(self, tmp_path, monkeypatch):
        """#4425"""
        monkeypatch.chdir(tmp_path)
        config = cast(Config, FakeConfig("hello"))
        t = TempPathFactory.from_config(config, _ispytest=True)
        assert t.getbasetemp().resolve() == (tmp_path / "hello").resolve()


class TestConfigTmpdir:
    def test_getbasetemp_custom_removes_old(self, pytester: Pytester) -> None:
        """
        def test_1(tmpdir):
        pass
        """

        mytemp = pytester.path.joinpath("xyz")
        p = pytester.makepyfile(
            """
            def test_1(tmpdir):
                pass
        """
        )
        pytester.runpytest(p, "--basetemp=%s" % mytemp)
        assert mytemp.exists()
        mytemp.joinpath("hello").touch()

        pytester.runpytest(p, "--basetemp=%s" % mytemp)
        assert mytemp.exists()
        assert not mytemp.joinpath("hello").exists()


testdata = [
    ("mypath", True),
    ("/mypath1", False),
    ("./mypath1", True),
    ("../mypath3", False),
    ("../../mypath4", False),
    ("mypath5/..", False),
    ("mypath6/../mypath6", True),
    ("mypath7/../mypath7/..", False),
]


@pytest.mark.parametrize("basename, is_ok", testdata)
def test_mktemp(pytester: Pytester, basename: str, is_ok: bool) -> None:
    """
    def test_abs_path(tmpdir_factory):
    tmpdir_factory.mktemp('{}', numbered=False)
    """

    mytemp = pytester.mkdir("mytemp")
    p = pytester.makepyfile(
        """
        def test_abs_path(tmpdir_factory):
            tmpdir_factory.mktemp('{}', numbered=False)
        """.format(
            basename
        )
    )

    result = pytester.runpytest(p, "--basetemp=%s" % mytemp)
    if is_ok:
        assert result.ret == 0
        assert mytemp.joinpath(basename).exists()
    else:
        assert result.ret == 1
        result.stdout.fnmatch_lines("*ValueError*")


def test_tmpdir_always_is_realpath(pytester: Pytester) -> None:
    """
    def test_1(tmpdir):
    import os
    assert os.path.realpath(str(tmpdir)) == str(tmpdir)
    """

    # the reason why tmpdir should be a realpath is that
    # when you cd to it and do "os.getcwd()" you will anyway
    # get the realpath.  Using the symlinked path can thus
    # easily result in path-inequality
    # XXX if that proves to be a problem, consider using
    # os.environ["PWD"]
    realtemp = pytester.mkdir("myrealtemp")
    linktemp = pytester.path.joinpath("symlinktemp")
    attempt_symlink_to(linktemp, str(realtemp))
    p = pytester.makepyfile(
        """
        def test_1(tmpdir):
            import os
            assert os.path.realpath(str(tmpdir)) == str(tmpdir)
    """
    )
    result = pytester.runpytest("-s", p, "--basetemp=%s/bt" % linktemp)
    assert not result.ret


def test_tmp_path_always_is_realpath(pytester: Pytester, monkeypatch) -> None:
    """
    def test_1(tmp_path):
    assert tmp_path.resolve() == tmp_path
    """

    # for reasoning see: test_tmpdir_always_is_realpath test-case
    realtemp = pytester.mkdir("myrealtemp")
    linktemp = pytester.path.joinpath("symlinktemp")
    attempt_symlink_to(linktemp, str(realtemp))
    monkeypatch.setenv("PYTEST_DEBUG_TEMPROOT", str(linktemp))
    pytester.makepyfile(
        """
        def test_1(tmp_path):
            assert tmp_path.resolve() == tmp_path
    """
    )
    reprec = pytester.inline_run()
    reprec.assertoutcome(passed=1)


def test_tmpdir_too_long_on_parametrization(pytester: Pytester) -> None:
    """
    import pytest
    @pytest.mark.parametrize("arg", ["1"*1000])
    def test_some(arg, tmpdir):
    tmpdir.ensure("hello")
    """

    pytester.makepyfile(
        """
        import pytest
        @pytest.mark.parametrize("arg", ["1"*1000])
        def test_some(arg, tmpdir):
            tmpdir.ensure("hello")
    """
    )
    reprec = pytester.inline_run()
    reprec.assertoutcome(passed=1)


def test_tmpdir_factory(pytester: Pytester) -> None:
    """
    import pytest
    @pytest.fixture(scope='session')
    def session_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('data', numbered=False)
    def test_some(session_dir):
    assert session_dir.isdir()
    """

    pytester.makepyfile(
        """
        import pytest
        @pytest.fixture(scope='session')
        def session_dir(tmpdir_factory):
            return tmpdir_factory.mktemp('data', numbered=False)
        def test_some(session_dir):
            assert session_dir.isdir()
    """
    )
    reprec = pytester.inline_run()
    reprec.assertoutcome(passed=1)


def test_tmpdir_fallback_tox_env(pytester: Pytester, monkeypatch) -> None:
    """Test that tmpdir works even if environment variables required by getpass
    module are missing (#1010).
    """
    monkeypatch.delenv("USER", raising=False)
    monkeypatch.delenv("USERNAME", raising=False)
    pytester.makepyfile(
        """
        def test_some(tmpdir):
            assert tmpdir.isdir()
    """
    )
    reprec = pytester.inline_run()
    reprec.assertoutcome(passed=1)


@pytest.fixture
def break_getuser(monkeypatch):
    """
    Simulate an environment where the user cannot be determined by either getuid or environment variables.
    
    This function sets the `os.getuid` function to return -1, indicating that the user cannot be determined by the operating system. It also removes any environment variables that could potentially contain the username (such as 'LOGNAME', 'USER', 'LNAME', and 'USERNAME').
    
    Args:
    monkeypatch (pytest.MonkeyPatch): A pytest fixture used to modify the behavior of functions and
    """

    monkeypatch.setattr("os.getuid", lambda: -1)
    # taken from python 2.7/3.4
    for envvar in ("LOGNAME", "USER", "LNAME", "USERNAME"):
        monkeypatch.delenv(envvar, raising=False)


@pytest.mark.usefixtures("break_getuser")
@pytest.mark.skipif(sys.platform.startswith("win"), reason="no os.getuid on windows")
def test_tmpdir_fallback_uid_not_found(pytester: Pytester) -> None:
    """Test that tmpdir works even if the current process's user id does not
    correspond to a valid user.
    """

    pytester.makepyfile(
        """
        def test_some(tmpdir):
            assert tmpdir.isdir()
    """
    )
    reprec = pytester.inline_run()
    reprec.assertoutcome(passed=1)


@pytest.mark.usefixtures("break_getuser")
@pytest.mark.skipif(sys.platform.startswith("win"), reason="no os.getuid on windows")
def test_get_user_uid_not_found():
    """Test that get_user() function works even if the current process's
    user id does not correspond to a valid user (e.g. running pytest in a
    Docker container with 'docker run -u'.
    """
    assert get_user() is None


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="win only")
def test_get_user(monkeypatch):
    """Test that get_user() function works even if environment variables
    required by getpass module are missing from the environment on Windows
    (#1010).
    """
    monkeypatch.delenv("USER", raising=False)
    monkeypatch.delenv("USERNAME", raising=False)
    assert get_user() is None


class TestNumberedDir:
    PREFIX = "fun-"

    def test_make(self, tmp_path):
        """
        Create numbered directories with a specified prefix in a temporary path.
        
        Args:
        tmp_path (Path): The base directory where the numbered directories will be created.
        
        Summary:
        This function creates 10 numbered directories with a specified prefix in the given temporary path. Each directory name starts with the prefix followed by a number from 0 to 9. It also checks if a symlink named 'current' exists and is a valid symlink pointing to one of the created directories.
        
        Returns:
        """

        for i in range(10):
            d = make_numbered_dir(root=tmp_path, prefix=self.PREFIX)
            assert d.name.startswith(self.PREFIX)
            assert d.name.endswith(str(i))

        symlink = tmp_path.joinpath(self.PREFIX + "current")
        if symlink.exists():
            # unix
            assert symlink.is_symlink()
            assert symlink.resolve() == d.resolve()

    def test_cleanup_lock_create(self, tmp_path):
        """
        Create and clean up a cleanup lock file.
        
        This function creates a directory and a cleanup lock file within it. It then attempts to create another lock file in the same directory, which should fail due to the existing lock. Finally, it unlinks the created lock file.
        
        Args:
        tmp_path (Path): A temporary path object provided by the pytest framework.
        
        Returns:
        None
        """

        d = tmp_path.joinpath("test")
        d.mkdir()
        lockfile = create_cleanup_lock(d)
        with pytest.raises(OSError, match="cannot create lockfile in .*"):
            create_cleanup_lock(d)

        lockfile.unlink()

    def test_lock_register_cleanup_removal(self, tmp_path: Path) -> None:
        """
        Test the cleanup lock removal functionality.
        
        This test ensures that the `create_cleanup_lock` function creates a lock file,
        and that the `register_cleanup_lock_removal` function correctly registers and
        removes the lock file when appropriate.
        
        Args:
        tmp_path (Path): A temporary directory path used for creating the lock file.
        
        Returns:
        None
        """

        lock = create_cleanup_lock(tmp_path)

        registry: List[Callable[..., None]] = []
        register_cleanup_lock_removal(lock, register=registry.append)

        (cleanup_func,) = registry

        assert lock.is_file()

        cleanup_func(original_pid="intentionally_different")

        assert lock.is_file()

        cleanup_func()

        assert not lock.exists()

        cleanup_func()

        assert not lock.exists()

    def _do_cleanup(self, tmp_path: Path) -> None:
        """
        Cleans up numbered directories within a specified temporary path.
        
        This method first calls `test_make` to create or modify files within the
        given `tmp_path`. Then, it uses `cleanup_numbered_dir` to remove all but
        the most recent two numbered directories, based on the provided `prefix`.
        The `keep` parameter is set to 2, indicating that only the last two
        directories should be retained. The `consider_lock_dead_if_created_before`
        parameter
        """

        self.test_make(tmp_path)
        cleanup_numbered_dir(
            root=tmp_path,
            prefix=self.PREFIX,
            keep=2,
            consider_lock_dead_if_created_before=0,
        )

    def test_cleanup_keep(self, tmp_path):
        """
        Cleans up temporary files in the specified directory `tmp_path`. The function iterates over the directory's contents, excluding symbolic links, and retains only two non-symlinks files. It then prints the paths of these two files.
        
        Args:
        tmp_path (pathlib.Path): The path to the temporary directory containing files to be cleaned up.
        
        Returns:
        None: This function does not return any value. It prints the paths of the two non-symlink files retained after
        """

        self._do_cleanup(tmp_path)
        a, b = (x for x in tmp_path.iterdir() if not x.is_symlink())
        print(a, b)

    def test_cleanup_locked(self, tmp_path):
        """
        Ensures that a directory is not deletable when a cleanup lock is present, but becomes deletable after a certain time threshold.
        
        Args:
        self: The instance of the class containing this method.
        tmp_path (pathlib.Path): A temporary directory path where the numbered directory will be created.
        
        Returns:
        None
        
        Summary:
        This function creates a numbered directory using `make_numbered_dir` and then creates a cleanup lock using `create_cleanup_lock`. It checks if the
        """

        p = make_numbered_dir(root=tmp_path, prefix=self.PREFIX)

        create_cleanup_lock(p)

        assert not pathlib.ensure_deletable(
            p, consider_lock_dead_if_created_before=p.stat().st_mtime - 1
        )
        assert pathlib.ensure_deletable(
            p, consider_lock_dead_if_created_before=p.stat().st_mtime + 1
        )

    def test_cleanup_ignores_symlink(self, tmp_path):
        """
        Test that cleanup ignores symlinks.
        
        Args:
        tmp_path (pathlib.Path): A temporary directory path.
        
        Summary:
        This function creates a symlink at `tmp_path/(PREFIX + 'current')` pointing to `tmp_path/(PREFIX + '5')`. It then calls `_do_cleanup(tmp_path)` to perform the cleanup operation, which should ignore the symlink.
        """

        the_symlink = tmp_path / (self.PREFIX + "current")
        attempt_symlink_to(the_symlink, tmp_path / (self.PREFIX + "5"))
        self._do_cleanup(tmp_path)

    def test_removal_accepts_lock(self, tmp_path):
        """
        Removes a numbered directory while ensuring a cleanup lock is respected.
        
        Args:
        tmp_path (pathlib.Path): Temporary path object representing the root directory.
        
        Summary:
        This function creates a numbered directory under `tmp_path` with a specified prefix, then attempts to delete it using `maybe_delete_a_numbered_dir`. A cleanup lock is created using `create_cleanup_lock` to prevent accidental deletion. The function asserts that the directory still exists after the attempted removal, indicating that the lock was
        """

        folder = make_numbered_dir(root=tmp_path, prefix=self.PREFIX)
        create_cleanup_lock(folder)
        maybe_delete_a_numbered_dir(folder)
        assert folder.is_dir()


class TestRmRf:
    def test_rm_rf(self, tmp_path):
        """
        Remove directory and its contents recursively.
        
        This function tests the removal of a directory and its contents using the `rm_rf` function. It creates a directory and verifies that it is removed, then creates a file within the directory and ensures that both the directory and the file are removed after calling `rm_rf`.
        
        Args:
        tmp_path (pathlib.Path): A temporary path object provided by the testing framework.
        
        Returns:
        None
        
        Example:
        >>> test_rm_rf(tmp_path)
        """

        adir = tmp_path / "adir"
        adir.mkdir()
        rm_rf(adir)

        assert not adir.exists()

        adir.mkdir()
        afile = adir / "afile"
        afile.write_bytes(b"aa")

        rm_rf(adir)
        assert not adir.exists()

    def test_rm_rf_with_read_only_file(self, tmp_path):
        """Ensure rm_rf can remove directories with read-only files in them (#5524)"""
        fn = tmp_path / "dir/foo.txt"
        fn.parent.mkdir()

        fn.touch()

        self.chmod_r(fn)

        rm_rf(fn.parent)

        assert not fn.parent.is_dir()

    def chmod_r(self, path):
        mode = os.stat(str(path)).st_mode
        os.chmod(str(path), mode & ~stat.S_IWRITE)

    def test_rm_rf_with_read_only_directory(self, tmp_path):
        """Ensure rm_rf can remove read-only directories (#5524)"""
        adir = tmp_path / "dir"
        adir.mkdir()

        (adir / "foo.txt").touch()
        self.chmod_r(adir)

        rm_rf(adir)

        assert not adir.is_dir()

    def test_on_rm_rf_error(self, tmp_path: Path) -> None:
        """
        Test the behavior of `on_rm_rf_error` function.
        
        This function tests the `on_rm_rf_error` function by simulating different error scenarios involving file removal operations. It creates a directory and a file within it, changes the file's permissions, and then attempts to remove the file using various methods and error conditions.
        
        Args:
        tmp_path (Path): A temporary path object used for creating and manipulating files and directories.
        
        Returns:
        None: The function does not return any value
        """

        adir = tmp_path / "dir"
        adir.mkdir()

        fn = adir / "foo.txt"
        fn.touch()
        self.chmod_r(fn)

        # unknown exception
        with pytest.warns(pytest.PytestWarning):
            exc_info1 = (None, RuntimeError(), None)
            on_rm_rf_error(os.unlink, str(fn), exc_info1, start_path=tmp_path)
            assert fn.is_file()

        # we ignore FileNotFoundError
        exc_info2 = (None, FileNotFoundError(), None)
        assert not on_rm_rf_error(None, str(fn), exc_info2, start_path=tmp_path)

        # unknown function
        with pytest.warns(
            pytest.PytestWarning,
            match=r"^\(rm_rf\) unknown function None when removing .*foo.txt:\nNone: ",
        ):
            exc_info3 = (None, PermissionError(), None)
            on_rm_rf_error(None, str(fn), exc_info3, start_path=tmp_path)
            assert fn.is_file()

        # ignored function
        with pytest.warns(None) as warninfo:
            exc_info4 = (None, PermissionError(), None)
            on_rm_rf_error(os.open, str(fn), exc_info4, start_path=tmp_path)
            assert fn.is_file()
        assert not [x.message for x in warninfo]

        exc_info5 = (None, PermissionError(), None)
        on_rm_rf_error(os.unlink, str(fn), exc_info5, start_path=tmp_path)
        assert not fn.is_file()


def attempt_symlink_to(path, to_path):
    """Try to make a symlink from "path" to "to_path", skipping in case this platform
    does not support it or we don't have sufficient privileges (common on Windows)."""
    try:
        Path(path).symlink_to(Path(to_path))
    except OSError:
        pytest.skip("could not create symbolic link")


def test_tmpdir_equals_tmp_path(tmpdir, tmp_path):
    assert Path(tmpdir) == tmp_path


def test_basetemp_with_read_only_files(pytester: Pytester) -> None:
    """Integration test for #5524"""
    pytester.makepyfile(
        """
        import os
        import stat

        def test(tmp_path):
            fn = tmp_path / 'foo.txt'
            fn.write_text('hello')
            mode = os.stat(str(fn)).st_mode
            os.chmod(str(fn), mode & ~stat.S_IREAD)
    """
    )
    result = pytester.runpytest("--basetemp=tmp")
    assert result.ret == 0
    # running a second time and ensure we don't crash
    result = pytester.runpytest("--basetemp=tmp")
    assert result.ret == 0
