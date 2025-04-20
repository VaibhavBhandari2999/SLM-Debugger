import os
import subprocess
import sys
import time
from typing import List

import py.path

import _pytest.pytester as pytester
import pytest
from _pytest.config import ExitCode
from _pytest.config import PytestPluginManager
from _pytest.pytester import CwdSnapshot
from _pytest.pytester import HookRecorder
from _pytest.pytester import LineMatcher
from _pytest.pytester import SysModulesSnapshot
from _pytest.pytester import SysPathsSnapshot
from _pytest.pytester import Testdir


def test_make_hook_recorder(testdir) -> None:
    """
    Tests the functionality of the `test_make_hook_recorder` function within the pytest framework.
    
    This function sets up a test item and a hook recorder, then logs various reports to the recorder to test its behavior. It verifies that the recorder correctly tracks passed, skipped, and failed outcomes, and that it can clear and unregister properly.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest Testdir object used to create and manage test items and configurations.
    
    Returns:
    - None: This function does not
    """

    item = testdir.getitem("def test_func(): pass")
    recorder = testdir.make_hook_recorder(item.config.pluginmanager)
    assert not recorder.getfailures()

    pytest.xfail("internal reportrecorder tests need refactoring")

    class rep:
        excinfo = None
        passed = False
        failed = True
        skipped = False
        when = "call"

    recorder.hook.pytest_runtest_logreport(report=rep)
    failures = recorder.getfailures()
    assert failures == [rep]
    failures = recorder.getfailures()
    assert failures == [rep]

    class rep2:
        excinfo = None
        passed = False
        failed = False
        skipped = True
        when = "call"

    rep2.passed = False
    rep2.skipped = True
    recorder.hook.pytest_runtest_logreport(report=rep2)

    modcol = testdir.getmodulecol("")
    rep3 = modcol.config.hook.pytest_make_collect_report(collector=modcol)
    rep3.passed = False
    rep3.failed = True
    rep3.skipped = False
    recorder.hook.pytest_collectreport(report=rep3)

    passed, skipped, failed = recorder.listoutcomes()
    assert not passed and skipped and failed

    numpassed, numskipped, numfailed = recorder.countoutcomes()
    assert numpassed == 0
    assert numskipped == 1
    assert numfailed == 1
    assert len(recorder.getfailedcollections()) == 1

    recorder.unregister()
    recorder.clear()
    recorder.hook.pytest_runtest_logreport(report=rep3)
    pytest.raises(ValueError, recorder.getfailures)


def test_parseconfig(testdir) -> None:
    config1 = testdir.parseconfig()
    config2 = testdir.parseconfig()
    assert config2 is not config1


def test_testdir_runs_with_plugin(testdir) -> None:
    testdir.makepyfile(
        """
        pytest_plugins = "pytester"
        def test_hello(testdir):
            assert 1
    """
    )
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


def test_testdir_with_doctest(testdir):
    """Check that testdir can be used within doctests.

    It used to use `request.function`, which is `None` with doctests."""
    testdir.makepyfile(
        **{
            "sub/t-doctest.py": """
        '''
        >>> import os
        >>> testdir = getfixture("testdir")
        >>> str(testdir.makepyfile("content")).replace(os.sep, '/')
        '.../basetemp/sub.t-doctest0/sub.py'
        '''
    """,
            "sub/__init__.py": "",
        }
    )
    result = testdir.runpytest(
        "-p", "pytester", "--doctest-modules", "sub/t-doctest.py"
    )
    assert result.ret == 0


def test_runresult_assertion_on_xfail(testdir) -> None:
    """
    Tests the behavior of the `test_runresult_assertion_on_xfail` function.
    
    This function creates a test file with a test marked as xfail that always fails. It then runs pytest on this test file and checks that the outcome is one xfailed test and that the return code is 0, indicating that the test run was successful.
    
    Parameters:
    testdir (pytest.Testdir): A pytest fixture that provides a temporary test directory.
    
    Returns:
    None: The function does not return anything
    """

    testdir.makepyfile(
        """
        import pytest

        pytest_plugins = "pytester"

        @pytest.mark.xfail
        def test_potato():
            assert False
    """
    )
    result = testdir.runpytest()
    result.assert_outcomes(xfailed=1)
    assert result.ret == 0


def test_runresult_assertion_on_xpassed(testdir) -> None:
    testdir.makepyfile(
        """
        import pytest

        pytest_plugins = "pytester"

        @pytest.mark.xfail
        def test_potato():
            assert True
    """
    )
    result = testdir.runpytest()
    result.assert_outcomes(xpassed=1)
    assert result.ret == 0


def test_xpassed_with_strict_is_considered_a_failure(testdir) -> None:
    testdir.makepyfile(
        """
        import pytest

        pytest_plugins = "pytester"

        @pytest.mark.xfail(strict=True)
        def test_potato():
            assert True
    """
    )
    result = testdir.runpytest()
    result.assert_outcomes(failed=1)
    assert result.ret != 0


def make_holder():
    """
    Generates a Python class and module with specific methods for testing purposes.
    
    This function creates a class `apiclass` with two methods `pytest_xyz` and `pytest_xyz_noarg`. It also creates a module `api` with the same methods. The methods are designed to be used in a testing context.
    
    Returns:
    tuple: A tuple containing the class `apiclass` and the module `api`.
    """

    class apiclass:
        def pytest_xyz(self, arg):
            "x"

        def pytest_xyz_noarg(self):
            "x"

    apimod = type(os)("api")

    def pytest_xyz(arg):
        "x"

    def pytest_xyz_noarg():
        "x"

    apimod.pytest_xyz = pytest_xyz  # type: ignore
    apimod.pytest_xyz_noarg = pytest_xyz_noarg  # type: ignore
    return apiclass, apimod


@pytest.mark.parametrize("holder", make_holder())
def test_hookrecorder_basic(holder) -> None:
    pm = PytestPluginManager()
    pm.add_hookspecs(holder)
    rec = HookRecorder(pm)
    pm.hook.pytest_xyz(arg=123)
    call = rec.popcall("pytest_xyz")
    assert call.arg == 123
    assert call._name == "pytest_xyz"
    pytest.raises(pytest.fail.Exception, rec.popcall, "abc")
    pm.hook.pytest_xyz_noarg()
    call = rec.popcall("pytest_xyz_noarg")
    assert call._name == "pytest_xyz_noarg"


def test_makepyfile_unicode(testdir) -> None:
    testdir.makepyfile(chr(0xFFFD))


def test_makepyfile_utf8(testdir) -> None:
    """Ensure makepyfile accepts utf-8 bytes as input (#2738)"""
    utf8_contents = """
        def setup_function(function):
            mixed_encoding = 'São Paulo'
    """.encode()
    p = testdir.makepyfile(utf8_contents)
    assert "mixed_encoding = 'São Paulo'".encode() in p.read("rb")


class TestInlineRunModulesCleanup:
    def test_inline_run_test_module_not_cleaned_up(self, testdir) -> None:
        """
        Test the inline run functionality for a test module that is not cleaned up properly.
        
        This test checks that the module is re-imported correctly and that the test results are as expected after modifying the test module.
        
        Parameters:
        testdir (pytest.Testdir): A pytest fixture that provides a temporary directory for test files.
        
        Returns:
        None: This function does not return any value. It asserts the expected behavior of the test module and its tests.
        """

        test_mod = testdir.makepyfile("def test_foo(): assert True")
        result = testdir.inline_run(str(test_mod))
        assert result.ret == ExitCode.OK
        # rewrite module, now test should fail if module was re-imported
        test_mod.write("def test_foo(): assert False")
        result2 = testdir.inline_run(str(test_mod))
        assert result2.ret == ExitCode.TESTS_FAILED

    def spy_factory(self):
        class SysModulesSnapshotSpy:
            instances = []  # type: List[SysModulesSnapshotSpy]

            def __init__(self, preserve=None) -> None:
                SysModulesSnapshotSpy.instances.append(self)
                self._spy_restore_count = 0
                self._spy_preserve = preserve
                self.__snapshot = SysModulesSnapshot(preserve=preserve)

            def restore(self):
                self._spy_restore_count += 1
                return self.__snapshot.restore()

        return SysModulesSnapshotSpy

    def test_inline_run_taking_and_restoring_a_sys_modules_snapshot(
        """
        Test the inline run functionality of pytest, which takes and restores a snapshot of sys.modules.
        
        This test function checks that when pytest runs a test file inline, it correctly takes a snapshot of the sys.modules dictionary, runs the tests, and then restores the original state of sys.modules.
        
        Parameters:
        testdir (pytest.Testdir): A pytest Testdir object used to create and run test files.
        monkeypatch (pytest.MonkeyPatch): A pytest MonkeyPatch object used to set the SysModulesSnapshot
        """

        self, testdir, monkeypatch
    ) -> None:
        spy_factory = self.spy_factory()
        monkeypatch.setattr(pytester, "SysModulesSnapshot", spy_factory)
        testdir.syspathinsert()
        original = dict(sys.modules)
        testdir.makepyfile(import1="# you son of a silly person")
        testdir.makepyfile(import2="# my hovercraft is full of eels")
        test_mod = testdir.makepyfile(
            """
            import import1
            def test_foo(): import import2"""
        )
        testdir.inline_run(str(test_mod))
        assert len(spy_factory.instances) == 1
        spy = spy_factory.instances[0]
        assert spy._spy_restore_count == 1
        assert sys.modules == original
        assert all(sys.modules[x] is original[x] for x in sys.modules)

    def test_inline_run_sys_modules_snapshot_restore_preserving_modules(
        self, testdir, monkeypatch
    ) -> None:
        spy_factory = self.spy_factory()
        monkeypatch.setattr(pytester, "SysModulesSnapshot", spy_factory)
        test_mod = testdir.makepyfile("def test_foo(): pass")
        testdir.inline_run(str(test_mod))
        spy = spy_factory.instances[0]
        assert not spy._spy_preserve("black_knight")
        assert spy._spy_preserve("zope")
        assert spy._spy_preserve("zope.interface")
        assert spy._spy_preserve("zopelicious")

    def test_external_test_module_imports_not_cleaned_up(self, testdir) -> None:
        testdir.syspathinsert()
        testdir.makepyfile(imported="data = 'you son of a silly person'")
        import imported

        test_mod = testdir.makepyfile(
            """
            def test_foo():
                import imported
                imported.data = 42"""
        )
        testdir.inline_run(str(test_mod))
        assert imported.data == 42


def test_assert_outcomes_after_pytest_error(testdir) -> None:
    testdir.makepyfile("def test_foo(): assert True")

    result = testdir.runpytest("--unexpected-argument")
    with pytest.raises(ValueError, match="Pytest terminal summary report not found"):
        result.assert_outcomes(passed=0)


def test_cwd_snapshot(testdir: Testdir) -> None:
    tmpdir = testdir.tmpdir
    foo = tmpdir.ensure("foo", dir=1)
    bar = tmpdir.ensure("bar", dir=1)
    foo.chdir()
    snapshot = CwdSnapshot()
    bar.chdir()
    assert py.path.local() == bar
    snapshot.restore()
    assert py.path.local() == foo


class TestSysModulesSnapshot:
    key = "my-test-module"

    def test_remove_added(self) -> None:
        original = dict(sys.modules)
        assert self.key not in sys.modules
        snapshot = SysModulesSnapshot()
        sys.modules[self.key] = "something"  # type: ignore
        assert self.key in sys.modules
        snapshot.restore()
        assert sys.modules == original

    def test_add_removed(self, monkeypatch) -> None:
        assert self.key not in sys.modules
        monkeypatch.setitem(sys.modules, self.key, "something")
        assert self.key in sys.modules
        original = dict(sys.modules)
        snapshot = SysModulesSnapshot()
        del sys.modules[self.key]
        assert self.key not in sys.modules
        snapshot.restore()
        assert sys.modules == original

    def test_restore_reloaded(self, monkeypatch) -> None:
        assert self.key not in sys.modules
        monkeypatch.setitem(sys.modules, self.key, "something")
        assert self.key in sys.modules
        original = dict(sys.modules)
        snapshot = SysModulesSnapshot()
        sys.modules[self.key] = "something else"  # type: ignore
        snapshot.restore()
        assert sys.modules == original

    def test_preserve_modules(self, monkeypatch) -> None:
        key = [self.key + str(i) for i in range(3)]
        assert not any(k in sys.modules for k in key)
        for i, k in enumerate(key):
            monkeypatch.setitem(sys.modules, k, "something" + str(i))
        original = dict(sys.modules)

        def preserve(name):
            return name in (key[0], key[1], "some-other-key")

        snapshot = SysModulesSnapshot(preserve=preserve)
        sys.modules[key[0]] = original[key[0]] = "something else0"  # type: ignore
        sys.modules[key[1]] = original[key[1]] = "something else1"  # type: ignore
        sys.modules[key[2]] = "something else2"  # type: ignore
        snapshot.restore()
        assert sys.modules == original

    def test_preserve_container(self, monkeypatch) -> None:
        original = dict(sys.modules)
        assert self.key not in original
        replacement = dict(sys.modules)
        replacement[self.key] = "life of brian"  # type: ignore
        snapshot = SysModulesSnapshot()
        monkeypatch.setattr(sys, "modules", replacement)
        snapshot.restore()
        assert sys.modules is replacement
        assert sys.modules == original


@pytest.mark.parametrize("path_type", ("path", "meta_path"))
class TestSysPathsSnapshot:
    other_path = {"path": "meta_path", "meta_path": "path"}

    @staticmethod
    def path(n: int) -> str:
        return "my-dirty-little-secret-" + str(n)

    def test_restore(self, monkeypatch, path_type) -> None:
        other_path_type = self.other_path[path_type]
        for i in range(10):
            assert self.path(i) not in getattr(sys, path_type)
        sys_path = [self.path(i) for i in range(6)]
        monkeypatch.setattr(sys, path_type, sys_path)
        original = list(sys_path)
        original_other = list(getattr(sys, other_path_type))
        snapshot = SysPathsSnapshot()
        transformation = {"source": (0, 1, 2, 3, 4, 5), "target": (6, 2, 9, 7, 5, 8)}
        assert sys_path == [self.path(x) for x in transformation["source"]]
        sys_path[1] = self.path(6)
        sys_path[3] = self.path(7)
        sys_path.append(self.path(8))
        del sys_path[4]
        sys_path[3:3] = [self.path(9)]
        del sys_path[0]
        assert sys_path == [self.path(x) for x in transformation["target"]]
        snapshot.restore()
        assert getattr(sys, path_type) is sys_path
        assert getattr(sys, path_type) == original
        assert getattr(sys, other_path_type) == original_other

    def test_preserve_container(self, monkeypatch, path_type) -> None:
        other_path_type = self.other_path[path_type]
        original_data = list(getattr(sys, path_type))
        original_other = getattr(sys, other_path_type)
        original_other_data = list(original_other)
        new = []  # type: List[object]
        snapshot = SysPathsSnapshot()
        monkeypatch.setattr(sys, path_type, new)
        snapshot.restore()
        assert getattr(sys, path_type) is new
        assert getattr(sys, path_type) == original_data
        assert getattr(sys, other_path_type) is original_other
        assert getattr(sys, other_path_type) == original_other_data


def test_testdir_subprocess(testdir) -> None:
    testfile = testdir.makepyfile("def test_one(): pass")
    assert testdir.runpytest_subprocess(testfile).ret == 0


def test_testdir_subprocess_via_runpytest_arg(testdir) -> None:
    """
    Tests the `testdir` fixture by running a test that uses subprocess to execute another test file. The test file contains a function that asserts the process ID of the test file is different from the process ID of the test running the subprocess.
    
    Key Parameters:
    - `testdir`: A pytest fixture that provides utilities for creating and running test files.
    
    Input:
    - A test file (`testfile`) is created within the test function, which contains another test function (`test_one`) that asserts the process ID
    """

    testfile = testdir.makepyfile(
        """
        def test_testdir_subprocess(testdir):
            import os
            testfile = testdir.makepyfile(
                \"""
                import os
                def test_one():
                    assert {} != os.getpid()
                \""".format(os.getpid())
            )
            assert testdir.runpytest(testfile).ret == 0
        """
    )
    result = testdir.runpytest_subprocess(
        "-p", "pytester", "--runpytest", "subprocess", testfile
    )
    assert result.ret == 0


def test_unicode_args(testdir) -> None:
    result = testdir.runpytest("-k", "אבג")
    assert result.ret == ExitCode.NO_TESTS_COLLECTED


def test_testdir_run_no_timeout(testdir) -> None:
    testfile = testdir.makepyfile("def test_no_timeout(): pass")
    assert testdir.runpytest_subprocess(testfile).ret == ExitCode.OK


def test_testdir_run_with_timeout(testdir) -> None:
    testfile = testdir.makepyfile("def test_no_timeout(): pass")

    timeout = 120

    start = time.time()
    result = testdir.runpytest_subprocess(testfile, timeout=timeout)
    end = time.time()
    duration = end - start

    assert result.ret == ExitCode.OK
    assert duration < timeout


def test_testdir_run_timeout_expires(testdir) -> None:
    testfile = testdir.makepyfile(
        """
        import time

        def test_timeout():
            time.sleep(10)"""
    )
    with pytest.raises(testdir.TimeoutExpired):
        testdir.runpytest_subprocess(testfile, timeout=1)


def test_linematcher_with_nonlist() -> None:
    """Test LineMatcher with regard to passing in a set (accidentally)."""
    from _pytest._code.source import Source

    lm = LineMatcher([])
    with pytest.raises(TypeError, match="invalid type for lines2: set"):
        lm.fnmatch_lines(set())  # type: ignore[arg-type]  # noqa: F821
    with pytest.raises(TypeError, match="invalid type for lines2: dict"):
        lm.fnmatch_lines({})  # type: ignore[arg-type]  # noqa: F821
    with pytest.raises(TypeError, match="invalid type for lines2: set"):
        lm.re_match_lines(set())  # type: ignore[arg-type]  # noqa: F821
    with pytest.raises(TypeError, match="invalid type for lines2: dict"):
        lm.re_match_lines({})  # type: ignore[arg-type]  # noqa: F821
    with pytest.raises(TypeError, match="invalid type for lines2: Source"):
        lm.fnmatch_lines(Source())  # type: ignore[arg-type]  # noqa: F821
    lm.fnmatch_lines([])
    lm.fnmatch_lines(())
    lm.fnmatch_lines("")
    assert lm._getlines({}) == {}  # type: ignore[arg-type,comparison-overlap]  # noqa: F821
    assert lm._getlines(set()) == set()  # type: ignore[arg-type,comparison-overlap]  # noqa: F821
    assert lm._getlines(Source()) == []
    assert lm._getlines(Source("pass\npass")) == ["pass", "pass"]


def test_linematcher_match_failure() -> None:
    """
    Test the LineMatcher's match failure functionality.
    
    This function tests the LineMatcher's ability to raise an exception when a match failure occurs using fnmatch or re.match patterns. It checks for both exact and pattern-based matches and ensures that unmatched lines are correctly identified.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    pytest.fail.Exception: If the match fails, an exception is raised with a detailed message indicating the mismatched lines and patterns.
    """

    lm = LineMatcher(["foo", "foo", "bar"])
    with pytest.raises(pytest.fail.Exception) as e:
        lm.fnmatch_lines(["foo", "f*", "baz"])
    assert e.value.msg is not None
    assert e.value.msg.splitlines() == [
        "exact match: 'foo'",
        "fnmatch: 'f*'",
        "   with: 'foo'",
        "nomatch: 'baz'",
        "    and: 'bar'",
        "remains unmatched: 'baz'",
    ]

    lm = LineMatcher(["foo", "foo", "bar"])
    with pytest.raises(pytest.fail.Exception) as e:
        lm.re_match_lines(["foo", "^f.*", "baz"])
    assert e.value.msg is not None
    assert e.value.msg.splitlines() == [
        "exact match: 'foo'",
        "re.match: '^f.*'",
        "    with: 'foo'",
        " nomatch: 'baz'",
        "     and: 'bar'",
        "remains unmatched: 'baz'",
    ]


def test_linematcher_consecutive():
    lm = LineMatcher(["1", "", "2"])
    with pytest.raises(pytest.fail.Exception) as excinfo:
        lm.fnmatch_lines(["1", "2"], consecutive=True)
    assert str(excinfo.value).splitlines() == [
        "exact match: '1'",
        "no consecutive match: '2'",
        "   with: ''",
    ]

    lm.re_match_lines(["1", r"\d?", "2"], consecutive=True)
    with pytest.raises(pytest.fail.Exception) as excinfo:
        lm.re_match_lines(["1", r"\d", "2"], consecutive=True)
    assert str(excinfo.value).splitlines() == [
        "exact match: '1'",
        r"no consecutive match: '\\d'",
        "    with: ''",
    ]


@pytest.mark.parametrize("function", ["no_fnmatch_line", "no_re_match_line"])
def test_linematcher_no_matching(function) -> None:
    """
    Test the LineMatcher object's functionality for non-matching patterns.
    
    This function tests the `LineMatcher` object's ability to handle non-matching patterns using two different methods: `fnmatch` and `re.match`. It checks for non-matching patterns twice to ensure the internal buffer is not affecting the results. The function supports two modes of operation based on the `function` parameter:
    - If `function` is "no_fnmatch_line", it uses `fnmatch` for pattern matching.
    """

    if function == "no_fnmatch_line":
        good_pattern = "*.py OK*"
        bad_pattern = "*X.py OK*"
    else:
        assert function == "no_re_match_line"
        good_pattern = r".*py OK"
        bad_pattern = r".*Xpy OK"

    lm = LineMatcher(
        [
            "cachedir: .pytest_cache",
            "collecting ... collected 1 item",
            "",
            "show_fixtures_per_test.py OK",
            "=== elapsed 1s ===",
        ]
    )

    # check the function twice to ensure we don't accumulate the internal buffer
    for i in range(2):
        with pytest.raises(pytest.fail.Exception) as e:
            func = getattr(lm, function)
            func(good_pattern)
        obtained = str(e.value).splitlines()
        if function == "no_fnmatch_line":
            assert obtained == [
                "nomatch: '{}'".format(good_pattern),
                "    and: 'cachedir: .pytest_cache'",
                "    and: 'collecting ... collected 1 item'",
                "    and: ''",
                "fnmatch: '{}'".format(good_pattern),
                "   with: 'show_fixtures_per_test.py OK'",
            ]
        else:
            assert obtained == [
                " nomatch: '{}'".format(good_pattern),
                "     and: 'cachedir: .pytest_cache'",
                "     and: 'collecting ... collected 1 item'",
                "     and: ''",
                "re.match: '{}'".format(good_pattern),
                "    with: 'show_fixtures_per_test.py OK'",
            ]

    func = getattr(lm, function)
    func(bad_pattern)  # bad pattern does not match any line: passes


def test_linematcher_no_matching_after_match() -> None:
    lm = LineMatcher(["1", "2", "3"])
    lm.fnmatch_lines(["1", "3"])
    with pytest.raises(pytest.fail.Exception) as e:
        lm.no_fnmatch_line("*")
    assert str(e.value).splitlines() == ["fnmatch: '*'", "   with: '1'"]


def test_pytester_addopts_before_testdir(request, monkeypatch) -> None:
    orig = os.environ.get("PYTEST_ADDOPTS", None)
    monkeypatch.setenv("PYTEST_ADDOPTS", "--orig-unused")
    testdir = request.getfixturevalue("testdir")
    assert "PYTEST_ADDOPTS" not in os.environ
    testdir.finalize()
    assert os.environ.get("PYTEST_ADDOPTS") == "--orig-unused"
    monkeypatch.undo()
    assert os.environ.get("PYTEST_ADDOPTS") == orig


def test_run_stdin(testdir) -> None:
    with pytest.raises(testdir.TimeoutExpired):
        testdir.run(
            sys.executable,
            "-c",
            "import sys, time; time.sleep(1); print(sys.stdin.read())",
            stdin=subprocess.PIPE,
            timeout=0.1,
        )

    with pytest.raises(testdir.TimeoutExpired):
        result = testdir.run(
            sys.executable,
            "-c",
            "import sys, time; time.sleep(1); print(sys.stdin.read())",
            stdin=b"input\n2ndline",
            timeout=0.1,
        )

    result = testdir.run(
        sys.executable,
        "-c",
        "import sys; print(sys.stdin.read())",
        stdin=b"input\n2ndline",
    )
    assert result.stdout.lines == ["input", "2ndline"]
    assert result.stderr.str() == ""
    assert result.ret == 0


def test_popen_stdin_pipe(testdir) -> None:
    """
    Test running a subprocess with a pipe for stdin.
    
    This function runs a Python subprocess using `sys.executable` to execute a command that reads from stdin. It then pipes input into the subprocess and checks the output and error streams. The function verifies that the input is correctly read and that the subprocess returns the expected output and exit code.
    
    Parameters:
    testdir (pytest.Testdir): A pytest test directory fixture used to run the subprocess.
    
    Returns:
    None: This function does not return any value
    """

    proc = testdir.popen(
        [sys.executable, "-c", "import sys; print(sys.stdin.read())"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
    )
    stdin = b"input\n2ndline"
    stdout, stderr = proc.communicate(input=stdin)
    assert stdout.decode("utf8").splitlines() == ["input", "2ndline"]
    assert stderr == b""
    assert proc.returncode == 0


def test_popen_stdin_bytes(testdir) -> None:
    proc = testdir.popen(
        [sys.executable, "-c", "import sys; print(sys.stdin.read())"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=b"input\n2ndline",
    )
    stdout, stderr = proc.communicate()
    assert stdout.decode("utf8").splitlines() == ["input", "2ndline"]
    assert stderr == b""
    assert proc.returncode == 0


def test_popen_default_stdin_stderr_and_stdin_None(testdir) -> None:
    # stdout, stderr default to pipes,
    # stdin can be None to not close the pipe, avoiding
    # "ValueError: flush of closed file" with `communicate()`.
    #
    # Wraps the test to make it not hang when run with "-s".
    p1 = testdir.makepyfile(
        '''
        import sys

        def test_inner(testdir):
            p1 = testdir.makepyfile(
                """
                import sys
                print(sys.stdin.read())  # empty
                print('stdout')
                sys.stderr.write('stderr')
                """
            )
            proc = testdir.popen([sys.executable, str(p1)], stdin=None)
            stdout, stderr = proc.communicate(b"ignored")
            assert stdout.splitlines() == [b"", b"stdout"]
            assert stderr.splitlines() == [b"stderr"]
            assert proc.returncode == 0
        '''
    )
    result = testdir.runpytest("-p", "pytester", str(p1))
    assert result.ret == 0


def test_spawn_uses_tmphome(testdir) -> None:
    tmphome = str(testdir.tmpdir)
    assert os.environ.get("HOME") == tmphome

    testdir.monkeypatch.setenv("CUSTOMENV", "42")

    p1 = testdir.makepyfile(
        """
        import os

        def test():
            assert os.environ["HOME"] == {tmphome!r}
            assert os.environ["CUSTOMENV"] == "42"
        """.format(
            tmphome=tmphome
        )
    )
    child = testdir.spawn_pytest(str(p1))
    out = child.read()
    assert child.wait() == 0, out.decode("utf8")


def test_run_result_repr() -> None:
    outlines = ["some", "normal", "output"]
    errlines = ["some", "nasty", "errors", "happened"]

    # known exit code
    r = pytester.RunResult(1, outlines, errlines, duration=0.5)
    assert (
        repr(r) == "<RunResult ret=ExitCode.TESTS_FAILED len(stdout.lines)=3"
        " len(stderr.lines)=4 duration=0.50s>"
    )

    # unknown exit code: just the number
    r = pytester.RunResult(99, outlines, errlines, duration=0.5)
    assert (
        repr(r) == "<RunResult ret=99 len(stdout.lines)=3"
        " len(stderr.lines)=4 duration=0.50s>"
    )


def test_testdir_outcomes_with_multiple_errors(testdir):
    """
    Test the testdir module's ability to handle multiple errors in test outcomes.
    
    This function runs a pytest test file with two test functions that both use a fixture which raises an exception. It verifies that pytest correctly identifies and counts the number of errors.
    
    Parameters:
    testdir (pytest.Testdir): A pytest fixture that provides a temporary test directory.
    
    Returns:
    None: The function asserts the outcome of the test run but does not return any value.
    
    Example Usage:
    >>> test_testdir_outcomes
    """

    p1 = testdir.makepyfile(
        """
        import pytest

        @pytest.fixture
        def bad_fixture():
            raise Exception("bad")

        def test_error1(bad_fixture):
            pass

        def test_error2(bad_fixture):
            pass
    """
    )
    result = testdir.runpytest(str(p1))
    result.assert_outcomes(error=2)

    assert result.parseoutcomes() == {"error": 2}


def test_makefile_joins_absolute_path(testdir: Testdir) -> None:
    absfile = testdir.tmpdir / "absfile"
    if sys.platform == "win32":
        with pytest.raises(OSError):
            testdir.makepyfile(**{str(absfile): ""})
    else:
        p1 = testdir.makepyfile(**{str(absfile): ""})
        assert str(p1) == (testdir.tmpdir / absfile) + ".py"
