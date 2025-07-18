"""(disabled by default) support for testing pytest and pytest plugins."""
import collections.abc
import gc
import importlib
import os
import platform
import re
import subprocess
import sys
import time
import traceback
from fnmatch import fnmatch
from io import StringIO
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union
from weakref import WeakKeyDictionary

import py

import pytest
from _pytest._code import Source
from _pytest._io.saferepr import saferepr
from _pytest.capture import MultiCapture
from _pytest.capture import SysCapture
from _pytest.fixtures import FixtureRequest
from _pytest.main import ExitCode
from _pytest.main import Session
from _pytest.monkeypatch import MonkeyPatch
from _pytest.pathlib import Path
from _pytest.reports import TestReport

if False:  # TYPE_CHECKING
    from typing import Type


IGNORE_PAM = [  # filenames added when obtaining details about the current user
    "/var/lib/sss/mc/passwd"
]


def pytest_addoption(parser):
    parser.addoption(
        "--lsof",
        action="store_true",
        dest="lsof",
        default=False,
        help="run FD checks if lsof is available",
    )

    parser.addoption(
        "--runpytest",
        default="inprocess",
        dest="runpytest",
        choices=("inprocess", "subprocess"),
        help=(
            "run pytest sub runs in tests using an 'inprocess' "
            "or 'subprocess' (python -m main) method"
        ),
    )

    parser.addini(
        "pytester_example_dir", help="directory to take the pytester example files from"
    )


def pytest_configure(config):
    if config.getvalue("lsof"):
        checker = LsofFdLeakChecker()
        if checker.matching_platform():
            config.pluginmanager.register(checker)

    config.addinivalue_line(
        "markers",
        "pytester_example_path(*path_segments): join the given path "
        "segments to `pytester_example_dir` for this test.",
    )


class LsofFdLeakChecker:
    def get_open_files(self):
        out = self._exec_lsof()
        open_files = self._parse_lsof_output(out)
        return open_files

    def _exec_lsof(self):
        pid = os.getpid()
        # py3: use subprocess.DEVNULL directly.
        with open(os.devnull, "wb") as devnull:
            return subprocess.check_output(
                ("lsof", "-Ffn0", "-p", str(pid)), stderr=devnull
            ).decode()

    def _parse_lsof_output(self, out):
        def isopen(line):
            return line.startswith("f") and (
                "deleted" not in line
                and "mem" not in line
                and "txt" not in line
                and "cwd" not in line
            )

        open_files = []

        for line in out.split("\n"):
            if isopen(line):
                fields = line.split("\0")
                fd = fields[0][1:]
                filename = fields[1][1:]
                if filename in IGNORE_PAM:
                    continue
                if filename.startswith("/"):
                    open_files.append((fd, filename))

        return open_files

    def matching_platform(self):
        try:
            subprocess.check_output(("lsof", "-v"))
        except (OSError, subprocess.CalledProcessError):
            return False
        else:
            return True

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_protocol(self, item):
        lines1 = self.get_open_files()
        yield
        if hasattr(sys, "pypy_version_info"):
            gc.collect()
        lines2 = self.get_open_files()

        new_fds = {t[0] for t in lines2} - {t[0] for t in lines1}
        leaked_files = [t for t in lines2 if t[0] in new_fds]
        if leaked_files:
            error = []
            error.append("***** %s FD leakage detected" % len(leaked_files))
            error.extend([str(f) for f in leaked_files])
            error.append("*** Before:")
            error.extend([str(f) for f in lines1])
            error.append("*** After:")
            error.extend([str(f) for f in lines2])
            error.append(error[0])
            error.append("*** function %s:%s: %s " % item.location)
            error.append("See issue #2366")
            item.warn(pytest.PytestWarning("\n".join(error)))


# used at least by pytest-xdist plugin


@pytest.fixture
def _pytest(request: FixtureRequest) -> "PytestArg":
    """Return a helper which offers a gethookrecorder(hook) method which
    returns a HookRecorder instance which helps to make assertions about called
    hooks.

    """
    return PytestArg(request)


class PytestArg:
    def __init__(self, request: FixtureRequest) -> None:
        self.request = request

    def gethookrecorder(self, hook) -> "HookRecorder":
        hookrecorder = HookRecorder(hook._pm)
        self.request.addfinalizer(hookrecorder.finish_recording)
        return hookrecorder


def get_public_names(values):
    """Only return names from iterator values without a leading underscore."""
    return [x for x in values if x[0] != "_"]


class ParsedCall:
    def __init__(self, name, kwargs):
        self.__dict__.update(kwargs)
        self._name = name

    def __repr__(self):
        d = self.__dict__.copy()
        del d["_name"]
        return "<ParsedCall {!r}(**{!r})>".format(self._name, d)

    if False:  # TYPE_CHECKING
        # The class has undetermined attributes, this tells mypy about it.
        def __getattr__(self, key):
            raise NotImplementedError()


class HookRecorder:
    """Record all hooks called in a plugin manager.

    This wraps all the hook calls in the plugin manager, recording each call
    before propagating the normal calls.

    """

    def __init__(self, pluginmanager) -> None:
        self._pluginmanager = pluginmanager
        self.calls = []  # type: List[ParsedCall]

        def before(hook_name: str, hook_impls, kwargs) -> None:
            self.calls.append(ParsedCall(hook_name, kwargs))

        def after(outcome, hook_name: str, hook_impls, kwargs) -> None:
            pass

        self._undo_wrapping = pluginmanager.add_hookcall_monitoring(before, after)

    def finish_recording(self) -> None:
        self._undo_wrapping()

    def getcalls(self, names: Union[str, Iterable[str]]) -> List[ParsedCall]:
        if isinstance(names, str):
            names = names.split()
        return [call for call in self.calls if call._name in names]

    def assert_contains(self, entries) -> None:
        __tracebackhide__ = True
        i = 0
        entries = list(entries)
        backlocals = sys._getframe(1).f_locals
        while entries:
            name, check = entries.pop(0)
            for ind, call in enumerate(self.calls[i:]):
                if call._name == name:
                    print("NAMEMATCH", name, call)
                    if eval(check, backlocals, call.__dict__):
                        print("CHECKERMATCH", repr(check), "->", call)
                    else:
                        print("NOCHECKERMATCH", repr(check), "-", call)
                        continue
                    i += ind + 1
                    break
                print("NONAMEMATCH", name, "with", call)
            else:
                pytest.fail("could not find {!r} check {!r}".format(name, check))

    def popcall(self, name: str) -> ParsedCall:
        __tracebackhide__ = True
        for i, call in enumerate(self.calls):
            if call._name == name:
                del self.calls[i]
                return call
        lines = ["could not find call {!r}, in:".format(name)]
        lines.extend(["  %s" % x for x in self.calls])
        pytest.fail("\n".join(lines))

    def getcall(self, name: str) -> ParsedCall:
        values = self.getcalls(name)
        assert len(values) == 1, (name, values)
        return values[0]

    # functionality for test reports

    def getreports(
        self,
        names: Union[
            str, Iterable[str]
        ] = "pytest_runtest_logreport pytest_collectreport",
    ) -> List[TestReport]:
        return [x.report for x in self.getcalls(names)]

    def matchreport(
        self,
        inamepart: str = "",
        names: Union[
            str, Iterable[str]
        ] = "pytest_runtest_logreport pytest_collectreport",
        when=None,
    ):
        """return a testreport whose dotted import path matches"""
        values = []
        for rep in self.getreports(names=names):
            if not when and rep.when != "call" and rep.passed:
                # setup/teardown passing reports - let's ignore those
                continue
            if when and rep.when != when:
                continue
            if not inamepart or inamepart in rep.nodeid.split("::"):
                values.append(rep)
        if not values:
            raise ValueError(
                "could not find test report matching %r: "
                "no test reports at all!" % (inamepart,)
            )
        if len(values) > 1:
            raise ValueError(
                "found 2 or more testreports matching {!r}: {}".format(
                    inamepart, values
                )
            )
        return values[0]

    def getfailures(
        self,
        names: Union[
            str, Iterable[str]
        ] = "pytest_runtest_logreport pytest_collectreport",
    ) -> List[TestReport]:
        return [rep for rep in self.getreports(names) if rep.failed]

    def getfailedcollections(self) -> List[TestReport]:
        return self.getfailures("pytest_collectreport")

    def listoutcomes(
        self
    ) -> Tuple[List[TestReport], List[TestReport], List[TestReport]]:
        passed = []
        skipped = []
        failed = []
        for rep in self.getreports("pytest_collectreport pytest_runtest_logreport"):
            if rep.passed:
                if rep.when == "call":
                    passed.append(rep)
            elif rep.skipped:
                skipped.append(rep)
            else:
                assert rep.failed, "Unexpected outcome: {!r}".format(rep)
                failed.append(rep)
        return passed, skipped, failed

    def countoutcomes(self) -> List[int]:
        return [len(x) for x in self.listoutcomes()]

    def assertoutcome(self, passed: int = 0, skipped: int = 0, failed: int = 0) -> None:
        realpassed, realskipped, realfailed = self.listoutcomes()
        assert passed == len(realpassed)
        assert skipped == len(realskipped)
        assert failed == len(realfailed)

    def clear(self) -> None:
        self.calls[:] = []


@pytest.fixture
def linecomp(request: FixtureRequest) -> "LineComp":
    return LineComp()


@pytest.fixture(name="LineMatcher")
def LineMatcher_fixture(request: FixtureRequest) -> "Type[LineMatcher]":
    return LineMatcher


@pytest.fixture
def testdir(request: FixtureRequest, tmpdir_factory) -> "Testdir":
    return Testdir(request, tmpdir_factory)


@pytest.fixture
def _sys_snapshot():
    snappaths = SysPathsSnapshot()
    snapmods = SysModulesSnapshot()
    yield
    snapmods.restore()
    snappaths.restore()


@pytest.fixture
def _config_for_test():
    from _pytest.config import get_config

    config = get_config()
    yield config
    config._ensure_unconfigure()  # cleanup, e.g. capman closing tmpfiles.


# regex to match the session duration string in the summary: "74.34s"
rex_session_duration = re.compile(r"\d+\.\d\ds")
# regex to match all the counts and phrases in the summary line: "34 passed, 111 skipped"
rex_outcome = re.compile(r"(\d+) (\w+)")


class RunResult:
    """The result of running a command.

    Attributes:

    :ivar ret: the return value
    :ivar outlines: list of lines captured from stdout
    :ivar errlines: list of lines captured from stderr
    :ivar stdout: :py:class:`LineMatcher` of stdout, use ``stdout.str()`` to
       reconstruct stdout or the commonly used ``stdout.fnmatch_lines()``
       method
    :ivar stderr: :py:class:`LineMatcher` of stderr
    :ivar duration: duration in seconds
    """

    def __init__(
        self,
        ret: Union[int, ExitCode],
        outlines: Sequence[str],
        errlines: Sequence[str],
        duration: float,
    ) -> None:
        try:
            self.ret = pytest.ExitCode(ret)  # type: Union[int, ExitCode]
        except ValueError:
            self.ret = ret
        self.outlines = outlines
        self.errlines = errlines
        self.stdout = LineMatcher(outlines)
        self.stderr = LineMatcher(errlines)
        self.duration = duration

    def __repr__(self) -> str:
        return (
            "<RunResult ret=%s len(stdout.lines)=%d len(stderr.lines)=%d duration=%.2fs>"
            % (self.ret, len(self.stdout.lines), len(self.stderr.lines), self.duration)
        )

    def parseoutcomes(self) -> Dict[str, int]:
        """Return a dictionary of outcomestring->num from parsing the terminal
        output that the test process produced.

        """
        for line in reversed(self.outlines):
            if rex_session_duration.search(line):
                outcomes = rex_outcome.findall(line)
                return {noun: int(count) for (count, noun) in outcomes}

        raise ValueError("Pytest terminal summary report not found")

    def assert_outcomes(
        self,
        passed: int = 0,
        skipped: int = 0,
        failed: int = 0,
        error: int = 0,
        xpassed: int = 0,
        xfailed: int = 0,
    ) -> None:
        """Assert that the specified outcomes appear with the respective
        numbers (0 means it didn't occur) in the text output from a test run.

        """
        d = self.parseoutcomes()
        obtained = {
            "passed": d.get("passed", 0),
            "skipped": d.get("skipped", 0),
            "failed": d.get("failed", 0),
            "error": d.get("error", 0),
            "xpassed": d.get("xpassed", 0),
            "xfailed": d.get("xfailed", 0),
        }
        expected = {
            "passed": passed,
            "skipped": skipped,
            "failed": failed,
            "error": error,
            "xpassed": xpassed,
            "xfailed": xfailed,
        }
        assert obtained == expected


class CwdSnapshot:
    def __init__(self) -> None:
        self.__saved = os.getcwd()

    def restore(self) -> None:
        os.chdir(self.__saved)


class SysModulesSnapshot:
    def __init__(self, preserve: Optional[Callable[[str], bool]] = None):
        self.__preserve = preserve
        self.__saved = dict(sys.modules)

    def restore(self) -> None:
        if self.__preserve:
            self.__saved.update(
                (k, m) for k, m in sys.modules.items() if self.__preserve(k)
            )
        sys.modules.clear()
        sys.modules.update(self.__saved)


class SysPathsSnapshot:
    def __init__(self) -> None:
        self.__saved = list(sys.path), list(sys.meta_path)

    def restore(self) -> None:
        sys.path[:], sys.meta_path[:] = self.__saved


class Testdir:
    """Temporary test directory with tools to test/run pytest itself.

    This is based on the ``tmpdir`` fixture but provides a number of methods
    which aid with testing pytest itself.  Unless :py:meth:`chdir` is used all
    methods will use :py:attr:`tmpdir` as their current working directory.

    Attributes:

    :ivar tmpdir: The :py:class:`py.path.local` instance of the temporary directory.

    :ivar plugins: A list of plugins to use with :py:meth:`parseconfig` and
       :py:meth:`runpytest`.  Initially this is an empty list but plugins can
       be added to the list.  The type of items to add to the list depends on
       the method using them so refer to them for details.

    """

    CLOSE_STDIN = object

    class TimeoutExpired(Exception):
        pass

    def __init__(self, request, tmpdir_factory):
        self.request = request
        self._mod_collections = WeakKeyDictionary()
        name = request.function.__name__
        self.tmpdir = tmpdir_factory.mktemp(name, numbered=True)
        self.test_tmproot = tmpdir_factory.mktemp("tmp-" + name, numbered=True)
        self.plugins = []
        self._cwd_snapshot = CwdSnapshot()
        self._sys_path_snapshot = SysPathsSnapshot()
        self._sys_modules_snapshot = self.__take_sys_modules_snapshot()
        self.chdir()
        self.request.addfinalizer(self.finalize)
        self._method = self.request.config.getoption("--runpytest")

        mp = self.monkeypatch = MonkeyPatch()
        mp.setenv("PYTEST_DEBUG_TEMPROOT", str(self.test_tmproot))
        # Ensure no unexpected caching via tox.
        mp.delenv("TOX_ENV_DIR", raising=False)
        # Discard outer pytest options.
        mp.delenv("PYTEST_ADDOPTS", raising=False)

        # Environment (updates) for inner runs.
        tmphome = str(self.tmpdir)
        self._env_run_update = {"HOME": tmphome, "USERPROFILE": tmphome}

    def __repr__(self):
        return "<Testdir {!r}>".format(self.tmpdir)

    def __str__(self):
        return str(self.tmpdir)

    def finalize(self):
        """Clean up global state artifacts.

        Some methods modify the global interpreter state and this tries to
        clean this up.  It does not remove the temporary directory however so
        it can be looked at after the test run has finished.

        """
        self._sys_modules_snapshot.restore()
        self._sys_path_snapshot.restore()
        self._cwd_snapshot.restore()
        self.monkeypatch.undo()

    def __take_sys_modules_snapshot(self):
        # some zope modules used by twisted-related tests keep internal state
        # and can't be deleted; we had some trouble in the past with
        # `zope.interface` for example
        def preserve_module(name):
            return name.startswith("zope")

        return SysModulesSnapshot(preserve=preserve_module)

    def make_hook_recorder(self, pluginmanager):
        """Create a new :py:class:`HookRecorder` for a PluginManager."""
        pluginmanager.reprec = reprec = HookRecorder(pluginmanager)
        self.request.addfinalizer(reprec.finish_recording)
        return reprec

    def chdir(self):
        """Cd into the temporary directory.

        This is done automatically upon instantiation.

        """
        self.tmpdir.chdir()

    def _makefile(self, ext, args, kwargs, encoding="utf-8"):
        items = list(kwargs.items())

        def to_text(s):
            return s.decode(encoding) if isinstance(s, bytes) else str(s)

        if args:
            source = "\n".join(to_text(x) for x in args)
            basename = self.request.function.__name__
            items.insert(0, (basename, source))

        ret = None
        for basename, value in items:
            p = self.tmpdir.join(basename).new(ext=ext)
            p.dirpath().ensure_dir()
            source = Source(value)
            source = "\n".join(to_text(line) for line in source.lines)
            p.write(source.strip().encode(encoding), "wb")
            if ret is None:
                ret = p
        return ret

    def makefile(self, ext, *args, **kwargs):
        r"""Create new file(s) in the testdir.

        :param str ext: The extension the file(s) should use, including the dot, e.g. `.py`.
        :param list[str] args: All args will be treated as strings and joined using newlines.
           The result will be written as contents to the file.  The name of the
           file will be based on the test function requesting this fixture.
        :param kwargs: Each keyword is the name of a file, while the value of it will
           be written as contents of the file.

        Examples:

        .. code-block:: python

            testdir.makefile(".txt", "line1", "line2")

            testdir.makefile(".ini", pytest="[pytest]\naddopts=-rs\n")

        """
        return self._makefile(ext, args, kwargs)

    def makeconftest(self, source):
        """Write a contest.py file with 'source' as contents."""
        return self.makepyfile(conftest=source)

    def makeini(self, source):
        """Write a tox.ini file with 'source' as contents."""
        return self.makefile(".ini", tox=source)

    def getinicfg(self, source):
        """Return the pytest section from the tox.ini config file."""
        p = self.makeini(source)
        return py.iniconfig.IniConfig(p)["pytest"]

    def makepyfile(self, *args, **kwargs):
        """Shortcut for .makefile() with a .py extension."""
        return self._makefile(".py", args, kwargs)

    def maketxtfile(self, *args, **kwargs):
        """Shortcut for .makefile() with a .txt extension."""
        return self._makefile(".txt", args, kwargs)

    def syspathinsert(self, path=None):
        """Prepend a directory to sys.path, defaults to :py:attr:`tmpdir`.

        This is undone automatically when this object dies at the end of each
        test.
        """
        if path is None:
            path = self.tmpdir

        self.monkeypatch.syspath_prepend(str(path))

    def mkdir(self, name):
        """Create a new (sub)directory."""
        return self.tmpdir.mkdir(name)

    def mkpydir(self, name):
        """Create a new python package.

        This creates a (sub)directory with an empty ``__init__.py`` file so it
        gets recognised as a python package.

        """
        p = self.mkdir(name)
        p.ensure("__init__.py")
        return p

    def copy_example(self, name=None):
        """Copy file from project's directory into the testdir.

        :param str name: The name of the file to copy.
        :return: path to the copied directory (inside ``self.tmpdir``).

        """
        import warnings
        from _pytest.warning_types import PYTESTER_COPY_EXAMPLE

        warnings.warn(PYTESTER_COPY_EXAMPLE, stacklevel=2)
        example_dir = self.request.config.getini("pytester_example_dir")
        if example_dir is None:
            raise ValueError("pytester_example_dir is unset, can't copy examples")
        example_dir = self.request.config.rootdir.join(example_dir)

        for extra_element in self.request.node.iter_markers("pytester_example_path"):
            assert extra_element.args
            example_dir = example_dir.join(*extra_element.args)

        if name is None:
            func_name = self.request.function.__name__
            maybe_dir = example_dir / func_name
            maybe_file = example_dir / (func_name + ".py")

            if maybe_dir.isdir():
                example_path = maybe_dir
            elif maybe_file.isfile():
                example_path = maybe_file
            else:
                raise LookupError(
                    "{} cant be found as module or package in {}".format(
                        func_name, example_dir.bestrelpath(self.request.config.rootdir)
                    )
                )
        else:
            example_path = example_dir.join(name)

        if example_path.isdir() and not example_path.join("__init__.py").isfile():
            example_path.copy(self.tmpdir)
            return self.tmpdir
        elif example_path.isfile():
            result = self.tmpdir.join(example_path.basename)
            example_path.copy(result)
            return result
        else:
            raise LookupError(
                'example "{}" is not found as a file or directory'.format(example_path)
            )

    Session = Session

    def getnode(self, config, arg):
        """Return the collection node of a file.

        :param config: :py:class:`_pytest.config.Config` instance, see
           :py:meth:`parseconfig` and :py:meth:`parseconfigure` to create the
           configuration

        :param arg: a :py:class:`py.path.local` instance of the file

        """
        session = Session(config)
        assert "::" not in str(arg)
        p = py.path.local(arg)
        config.hook.pytest_sessionstart(session=session)
        res = session.perform_collect([str(p)], genitems=False)[0]
        config.hook.pytest_sessionfinish(session=session, exitstatus=ExitCode.OK)
        return res

    def getpathnode(self, path):
        """Return the collection node of a file.

        This is like :py:meth:`getnode` but uses :py:meth:`parseconfigure` to
        create the (configured) pytest Config instance.

        :param path: a :py:class:`py.path.local` instance of the file

        """
        config = self.parseconfigure(path)
        session = Session(config)
        x = session.fspath.bestrelpath(path)
        config.hook.pytest_sessionstart(session=session)
        res = session.perform_collect([x], genitems=False)[0]
        config.hook.pytest_sessionfinish(session=session, exitstatus=ExitCode.OK)
        return res

    def genitems(self, colitems):
        """Generate all test items from a collection node.

        This recurses into the collection node and returns a list of all the
        test items contained within.

        """
        session = colitems[0].session
        result = []
        for colitem in colitems:
            result.extend(session.genitems(colitem))
        return result

    def runitem(self, source):
        """Run the "test_func" Item.

        The calling test instance (class containing the test method) must
        provide a ``.getrunner()`` method which should return a runner which
        can run the test protocol for a single item, e.g.
        :py:func:`_pytest.runner.runtestprotocol`.

        """
        # used from runner functional tests
        item = self.getitem(source)
        # the test class where we are called from wants to provide the runner
        testclassinstance = self.request.instance
        runner = testclassinstance.getrunner()
        return runner(item)

    def inline_runsource(self, source, *cmdlineargs):
        """Run a test module in process using ``pytest.main()``.

        This run writes "source" into a temporary file and runs
        ``pytest.main()`` on it, returning a :py:class:`HookRecorder` instance
        for the result.

        :param source: the source code of the test module

        :param cmdlineargs: any extra command line arguments to use

        :return: :py:class:`HookRecorder` instance of the result

        """
        p = self.makepyfile(source)
        values = list(cmdlineargs) + [p]
        return self.inline_run(*values)

    def inline_genitems(self, *args):
        """Run ``pytest.main(['--collectonly'])`` in-process.

        Runs the :py:func:`pytest.main` function to run all of pytest inside
        the test process itself like :py:meth:`inline_run`, but returns a
        tuple of the collected items and a :py:class:`HookRecorder` instance.

        """
        rec = self.inline_run("--collect-only", *args)
        items = [x.item for x in rec.getcalls("pytest_itemcollected")]
        return items, rec

    def inline_run(self, *args, plugins=(), no_reraise_ctrlc=False):
        """Run ``pytest.main()`` in-process, returning a HookRecorder.

        Runs the :py:func:`pytest.main` function to run all of pytest inside
        the test process itself.  This means it can return a
        :py:class:`HookRecorder` instance which gives more detailed results
        from that run than can be done by matching stdout/stderr from
        :py:meth:`runpytest`.

        :param args: command line arguments to pass to :py:func:`pytest.main`

        :kwarg plugins: extra plugin instances the ``pytest.main()`` instance should use.

        :kwarg no_reraise_ctrlc: typically we reraise keyboard interrupts from the child run. If
            True, the KeyboardInterrupt exception is captured.

        :return: a :py:class:`HookRecorder` instance
        """
        # (maybe a cpython bug?) the importlib cache sometimes isn't updated
        # properly between file creation and inline_run (especially if imports
        # are interspersed with file creation)
        importlib.invalidate_caches()

        plugins = list(plugins)
        finalizers = []
        try:
            # Do not load user config (during runs only).
            mp_run = MonkeyPatch()
            for k, v in self._env_run_update.items():
                mp_run.setenv(k, v)
            finalizers.append(mp_run.undo)

            # Any sys.module or sys.path changes done while running pytest
            # inline should be reverted after the test run completes to avoid
            # clashing with later inline tests run within the same pytest test,
            # e.g. just because they use matching test module names.
            finalizers.append(self.__take_sys_modules_snapshot().restore)
            finalizers.append(SysPathsSnapshot().restore)

            # Important note:
            # - our tests should not leave any other references/registrations
            #   laying around other than possibly loaded test modules
            #   referenced from sys.modules, as nothing will clean those up
            #   automatically

            rec = []

            class Collect:
                def pytest_configure(x, config):
                    rec.append(self.make_hook_recorder(config.pluginmanager))

            plugins.append(Collect())
            ret = pytest.main(list(args), plugins=plugins)
            if len(rec) == 1:
                reprec = rec.pop()
            else:

                class reprec:  # type: ignore
                    pass

            reprec.ret = ret

            # typically we reraise keyboard interrupts from the child run
            # because it's our user requesting interruption of the testing
            if ret == ExitCode.INTERRUPTED and not no_reraise_ctrlc:
                calls = reprec.getcalls("pytest_keyboard_interrupt")
                if calls and calls[-1].excinfo.type == KeyboardInterrupt:
                    raise KeyboardInterrupt()
            return reprec
        finally:
            for finalizer in finalizers:
                finalizer()

    def runpytest_inprocess(self, *args, **kwargs) -> RunResult:
        """Return result of running pytest in-process, providing a similar
        interface to what self.runpytest() provides.
        """
        syspathinsert = kwargs.pop("syspathinsert", False)

        if syspathinsert:
            self.syspathinsert()
        now = time.time()
        capture = MultiCapture(Capture=SysCapture)
        capture.start_capturing()
        try:
            try:
                reprec = self.inline_run(*args, **kwargs)
            except SystemExit as e:
                ret = e.args[0]
                try:
                    ret = ExitCode(e.args[0])
                except ValueError:
                    pass

                class reprec:  # type: ignore
                    ret = ret

            except Exception:
                traceback.print_exc()

                class reprec:  # type: ignore
                    ret = ExitCode(3)

        finally:
            out, err = capture.readouterr()
            capture.stop_capturing()
            sys.stdout.write(out)
            sys.stderr.write(err)

        res = RunResult(
            reprec.ret, out.splitlines(), err.splitlines(), time.time() - now
        )
        res.reprec = reprec  # type: ignore
        return res

    def runpytest(self, *args, **kwargs) -> RunResult:
        """Run pytest inline or in a subprocess, depending on the command line
        option "--runpytest" and return a :py:class:`RunResult`.

        """
        args = self._ensure_basetemp(args)
        if self._method == "inprocess":
            return self.runpytest_inprocess(*args, **kwargs)
        elif self._method == "subprocess":
            return self.runpytest_subprocess(*args, **kwargs)
        raise RuntimeError("Unrecognized runpytest option: {}".format(self._method))

    def _ensure_basetemp(self, args):
        args = list(args)
        for x in args:
            if str(x).startswith("--basetemp"):
                break
        else:
            args.append("--basetemp=%s" % self.tmpdir.dirpath("basetemp"))
        return args

    def parseconfig(self, *args):
        """Return a new pytest Config instance from given commandline args.

        This invokes the pytest bootstrapping code in _pytest.config to create
        a new :py:class:`_pytest.core.PluginManager` and call the
        pytest_cmdline_parse hook to create a new
        :py:class:`_pytest.config.Config` instance.

        If :py:attr:`plugins` has been populated they should be plugin modules
        to be registered with the PluginManager.

        """
        args = self._ensure_basetemp(args)

        import _pytest.config

        config = _pytest.config._prepareconfig(args, self.plugins)
        # we don't know what the test will do with this half-setup config
        # object and thus we make sure it gets unconfigured properly in any
        # case (otherwise capturing could still be active, for example)
        self.request.addfinalizer(config._ensure_unconfigure)
        return config

    def parseconfigure(self, *args):
        """Return a new pytest configured Config instance.

        This returns a new :py:class:`_pytest.config.Config` instance like
        :py:meth:`parseconfig`, but also calls the pytest_configure hook.
        """
        config = self.parseconfig(*args)
        config._do_configure()
        return config

    def getitem(self, source, funcname="test_func"):
        """Return the test item for a test function.

        This writes the source to a python file and runs pytest's collection on
        the resulting module, returning the test item for the requested
        function name.

        :param source: the module source

        :param funcname: the name of the test function for which to return a
            test item

        """
        items = self.getitems(source)
        for item in items:
            if item.name == funcname:
                return item
        assert 0, "{!r} item not found in module:\n{}\nitems: {}".format(
            funcname, source, items
        )

    def getitems(self, source):
        """Return all test items collected from the module.

        This writes the source to a python file and runs pytest's collection on
        the resulting module, returning all test items contained within.

        """
        modcol = self.getmodulecol(source)
        return self.genitems([modcol])

    def getmodulecol(self, source, configargs=(), withinit=False):
        """Return the module collection node for ``source``.

        This writes ``source`` to a file using :py:meth:`makepyfile` and then
        runs the pytest collection on it, returning the collection node for the
        test module.

        :param source: the source code of the module to collect

        :param configargs: any extra arguments to pass to
            :py:meth:`parseconfigure`

        :param withinit: whether to also write an ``__init__.py`` file to the
            same directory to ensure it is a package

        """
        if isinstance(source, Path):
            path = self.tmpdir.join(str(source))
            assert not withinit, "not supported for paths"
        else:
            kw = {self.request.function.__name__: Source(source).strip()}
            path = self.makepyfile(**kw)
        if withinit:
            self.makepyfile(__init__="#")
        self.config = config = self.parseconfigure(path, *configargs)
        return self.getnode(config, path)

    def collect_by_name(self, modcol, name):
        """Return the collection node for name from the module collection.

        This will search a module collection node for a collection node
        matching the given name.

        :param modcol: a module collection node; see :py:meth:`getmodulecol`

        :param name: the name of the node to return

        """
        if modcol not in self._mod_collections:
            self._mod_collections[modcol] = list(modcol.collect())
        for colitem in self._mod_collections[modcol]:
            if colitem.name == name:
                return colitem

    def popen(
        self,
        cmdargs,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=CLOSE_STDIN,
        **kw
    ):
        """Invoke subprocess.Popen.

        This calls subprocess.Popen making sure the current working directory
        is in the PYTHONPATH.

        You probably want to use :py:meth:`run` instead.

        """
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(
            filter(None, [os.getcwd(), env.get("PYTHONPATH", "")])
        )
        env.update(self._env_run_update)
        kw["env"] = env

        if stdin is Testdir.CLOSE_STDIN:
            kw["stdin"] = subprocess.PIPE
        elif isinstance(stdin, bytes):
            kw["stdin"] = subprocess.PIPE
        else:
            kw["stdin"] = stdin

        popen = subprocess.Popen(cmdargs, stdout=stdout, stderr=stderr, **kw)
        if stdin is Testdir.CLOSE_STDIN:
            popen.stdin.close()
        elif isinstance(stdin, bytes):
            popen.stdin.write(stdin)

        return popen

    def run(self, *cmdargs, timeout=None, stdin=CLOSE_STDIN) -> RunResult:
        """Run a command with arguments.

        Run a process using subprocess.Popen saving the stdout and stderr.

        :param args: the sequence of arguments to pass to `subprocess.Popen()`
        :kwarg timeout: the period in seconds after which to timeout and raise
            :py:class:`Testdir.TimeoutExpired`
        :kwarg stdin: optional standard input.  Bytes are being send, closing
            the pipe, otherwise it is passed through to ``popen``.
            Defaults to ``CLOSE_STDIN``, which translates to using a pipe
            (``subprocess.PIPE``) that gets closed.

        Returns a :py:class:`RunResult`.

        """
        __tracebackhide__ = True

        cmdargs = tuple(
            str(arg) if isinstance(arg, py.path.local) else arg for arg in cmdargs
        )
        p1 = self.tmpdir.join("stdout")
        p2 = self.tmpdir.join("stderr")
        print("running:", *cmdargs)
        print("     in:", py.path.local())
        f1 = open(str(p1), "w", encoding="utf8")
        f2 = open(str(p2), "w", encoding="utf8")
        try:
            now = time.time()
            popen = self.popen(
                cmdargs,
                stdin=stdin,
                stdout=f1,
                stderr=f2,
                close_fds=(sys.platform != "win32"),
            )
            if isinstance(stdin, bytes):
                popen.stdin.close()

            def handle_timeout():
                __tracebackhide__ = True

                timeout_message = (
                    "{seconds} second timeout expired running:"
                    " {command}".format(seconds=timeout, command=cmdargs)
                )

                popen.kill()
                popen.wait()
                raise self.TimeoutExpired(timeout_message)

            if timeout is None:
                ret = popen.wait()
            else:
                try:
                    ret = popen.wait(timeout)
                except subprocess.TimeoutExpired:
                    handle_timeout()
        finally:
            f1.close()
            f2.close()
        f1 = open(str(p1), "r", encoding="utf8")
        f2 = open(str(p2), "r", encoding="utf8")
        try:
            out = f1.read().splitlines()
            err = f2.read().splitlines()
        finally:
            f1.close()
            f2.close()
        self._dump_lines(out, sys.stdout)
        self._dump_lines(err, sys.stderr)
        try:
            ret = ExitCode(ret)
        except ValueError:
            pass
        return RunResult(ret, out, err, time.time() - now)

    def _dump_lines(self, lines, fp):
        try:
            for line in lines:
                print(line, file=fp)
        except UnicodeEncodeError:
            print("couldn't print to {} because of encoding".format(fp))

    def _getpytestargs(self):
        return sys.executable, "-mpytest"

    def runpython(self, script) -> RunResult:
        """Run a python script using sys.executable as interpreter.

        Returns a :py:class:`RunResult`.

        """
        return self.run(sys.executable, script)

    def runpython_c(self, command):
        """Run python -c "command", return a :py:class:`RunResult`."""
        return self.run(sys.executable, "-c", command)

    def runpytest_subprocess(self, *args, timeout=None) -> RunResult:
        """Run pytest as a subprocess with given arguments.

        Any plugins added to the :py:attr:`plugins` list will be added using the
        ``-p`` command line option.  Additionally ``--basetemp`` is used to put
        any temporary files and directories in a numbered directory prefixed
        with "runpytest-" to not conflict with the normal numbered pytest
        location for temporary files and directories.

        :param args: the sequence of arguments to pass to the pytest subprocess
        :param timeout: the period in seconds after which to timeout and raise
            :py:class:`Testdir.TimeoutExpired`

        Returns a :py:class:`RunResult`.
        """
        __tracebackhide__ = True
        p = py.path.local.make_numbered_dir(
            prefix="runpytest-", keep=None, rootdir=self.tmpdir
        )
        args = ("--basetemp=%s" % p,) + args
        plugins = [x for x in self.plugins if isinstance(x, str)]
        if plugins:
            args = ("-p", plugins[0]) + args
        args = self._getpytestargs() + args
        return self.run(*args, timeout=timeout)

    def spawn_pytest(self, string, expect_timeout=10.0):
        """Run pytest using pexpect.

        This makes sure to use the right pytest and sets up the temporary
        directory locations.

        The pexpect child is returned.

        """
        basetemp = self.tmpdir.mkdir("temp-pexpect")
        invoke = " ".join(map(str, self._getpytestargs()))
        cmd = "{} --basetemp={} {}".format(invoke, basetemp, string)
        return self.spawn(cmd, expect_timeout=expect_timeout)

    def spawn(self, cmd, expect_timeout=10.0):
        """Run a command using pexpect.

        The pexpect child is returned.

        """
        pexpect = pytest.importorskip("pexpect", "3.0")
        if hasattr(sys, "pypy_version_info") and "64" in platform.machine():
            pytest.skip("pypy-64 bit not supported")
        if not hasattr(pexpect, "spawn"):
            pytest.skip("pexpect.spawn not available")
        logfile = self.tmpdir.join("spawn.out").open("wb")

        # Do not load user config.
        env = os.environ.copy()
        env.update(self._env_run_update)

        child = pexpect.spawn(cmd, logfile=logfile, env=env)
        self.request.addfinalizer(logfile.close)
        child.timeout = expect_timeout
        return child


def getdecoded(out):
    try:
        return out.decode("utf-8")
    except UnicodeDecodeError:
        return "INTERNAL not-utf8-decodeable, truncated string:\n{}".format(
            saferepr(out)
        )


class LineComp:
    def __init__(self):
        self.stringio = StringIO()

    def assert_contains_lines(self, lines2):
        """Assert that lines2 are contained (linearly) in lines1.

        Return a list of extralines found.

        """
        __tracebackhide__ = True
        val = self.stringio.getvalue()
        self.stringio.truncate(0)
        self.stringio.seek(0)
        lines1 = val.split("\n")
        return LineMatcher(lines1).fnmatch_lines(lines2)


class LineMatcher:
    """Flexible matching of text.

    This is a convenience class to test large texts like the output of
    commands.

    The constructor takes a list of lines without their trailing newlines, i.e.
    ``text.splitlines()``.

    """

    def __init__(self, lines):
        self.lines = lines
        self._log_output = []

    def str(self):
        """Return the entire original text."""
        return "\n".join(self.lines)

    def _getlines(self, lines2):
        if isinstance(lines2, str):
            lines2 = Source(lines2)
        if isinstance(lines2, Source):
            lines2 = lines2.strip().lines
        return lines2

    def fnmatch_lines_random(self, lines2):
        """Check lines exist in the output using in any order.

        Lines are checked using ``fnmatch.fnmatch``. The argument is a list of
        lines which have to occur in the output, in any order.

        """
        self._match_lines_random(lines2, fnmatch)

    def re_match_lines_random(self, lines2):
        """Check lines exist in the output using ``re.match``, in any order.

        The argument is a list of lines which have to occur in the output, in
        any order.

        """
        self._match_lines_random(lines2, lambda name, pat: re.match(pat, name))

    def _match_lines_random(self, lines2, match_func):
        """Check lines exist in the output.

        The argument is a list of lines which have to occur in the output, in
        any order.  Each line can contain glob whildcards.

        """
        lines2 = self._getlines(lines2)
        for line in lines2:
            for x in self.lines:
                if line == x or match_func(x, line):
                    self._log("matched: ", repr(line))
                    break
            else:
                self._log("line %r not found in output" % line)
                raise ValueError(self._log_text)

    def get_lines_after(self, fnline):
        """Return all lines following the given line in the text.

        The given line can contain glob wildcards.

        """
        for i, line in enumerate(self.lines):
            if fnline == line or fnmatch(line, fnline):
                return self.lines[i + 1 :]
        raise ValueError("line %r not found in output" % fnline)

    def _log(self, *args):
        self._log_output.append(" ".join(str(x) for x in args))

    @property
    def _log_text(self):
        return "\n".join(self._log_output)

    def fnmatch_lines(self, lines2):
        """Search captured text for matching lines using ``fnmatch.fnmatch``.

        The argument is a list of lines which have to match and can use glob
        wildcards.  If they do not match a pytest.fail() is called.  The
        matches and non-matches are also shown as part of the error message.
        """
        __tracebackhide__ = True
        self._match_lines(lines2, fnmatch, "fnmatch")

    def re_match_lines(self, lines2):
        """Search captured text for matching lines using ``re.match``.

        The argument is a list of lines which have to match using ``re.match``.
        If they do not match a pytest.fail() is called.

        The matches and non-matches are also shown as part of the error message.
        """
        __tracebackhide__ = True
        self._match_lines(lines2, lambda name, pat: re.match(pat, name), "re.match")

    def _match_lines(self, lines2, match_func, match_nickname):
        """Underlying implementation of ``fnmatch_lines`` and ``re_match_lines``.

        :param list[str] lines2: list of string patterns to match. The actual
            format depends on ``match_func``
        :param match_func: a callable ``match_func(line, pattern)`` where line
            is the captured line from stdout/stderr and pattern is the matching
            pattern
        :param str match_nickname: the nickname for the match function that
            will be logged to stdout when a match occurs
        """
        assert isinstance(lines2, collections.abc.Sequence)
        lines2 = self._getlines(lines2)
        lines1 = self.lines[:]
        nextline = None
        extralines = []
        __tracebackhide__ = True
        wnick = len(match_nickname) + 1
        for line in lines2:
            nomatchprinted = False
            while lines1:
                nextline = lines1.pop(0)
                if line == nextline:
                    self._log("exact match:", repr(line))
                    break
                elif match_func(nextline, line):
                    self._log("%s:" % match_nickname, repr(line))
                    self._log(
                        "{:>{width}}".format("with:", width=wnick), repr(nextline)
                    )
                    break
                else:
                    if not nomatchprinted:
                        self._log(
                            "{:>{width}}".format("nomatch:", width=wnick), repr(line)
                        )
                        nomatchprinted = True
                    self._log("{:>{width}}".format("and:", width=wnick), repr(nextline))
                extralines.append(nextline)
            else:
                self._log("remains unmatched: {!r}".format(line))
                pytest.fail(self._log_text.lstrip())

    def no_fnmatch_line(self, pat):
        """Ensure captured lines do not match the given pattern, using ``fnmatch.fnmatch``.

        :param str pat: the pattern to match lines.
        """
        __tracebackhide__ = True
        self._no_match_line(pat, fnmatch, "fnmatch")

    def no_re_match_line(self, pat):
        """Ensure captured lines do not match the given pattern, using ``re.match``.

        :param str pat: the regular expression to match lines.
        """
        __tracebackhide__ = True
        self._no_match_line(pat, lambda name, pat: re.match(pat, name), "re.match")

    def _no_match_line(self, pat, match_func, match_nickname):
        """Ensure captured lines does not have a the given pattern, using ``fnmatch.fnmatch``

        :param str pat: the pattern to match lines
        """
        __tracebackhide__ = True
        nomatch_printed = False
        wnick = len(match_nickname) + 1
        try:
            for line in self.lines:
                if match_func(line, pat):
                    self._log("%s:" % match_nickname, repr(pat))
                    self._log("{:>{width}}".format("with:", width=wnick), repr(line))
                    pytest.fail(self._log_text.lstrip())
                else:
                    if not nomatch_printed:
                        self._log(
                            "{:>{width}}".format("nomatch:", width=wnick), repr(pat)
                        )
                        nomatch_printed = True
                    self._log("{:>{width}}".format("and:", width=wnick), repr(line))
        finally:
            self._log_output = []
