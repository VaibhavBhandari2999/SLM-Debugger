import os
import re
import sys
import textwrap

import pytest
from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture
def mp():
    """
    Context Manager for Monkey Patching:
    This context manager temporarily modifies the system path and current working directory to allow for monkey patching operations.
    
    Key Parameters:
    - None
    
    Yields:
    - MonkeyPatch: An instance of MonkeyPatch that can be used to apply monkey patching.
    
    Usage:
    with mp():
    # Code that uses monkey patching
    pass
    
    This context manager ensures that the system path and current working directory are restored to their original states after the operations are completed.
    """

    cwd = os.getcwd()
    sys_path = list(sys.path)
    yield MonkeyPatch()
    sys.path[:] = sys_path
    os.chdir(cwd)


def test_setattr():
    class A:
        x = 1

    monkeypatch = MonkeyPatch()
    pytest.raises(AttributeError, monkeypatch.setattr, A, "notexists", 2)
    monkeypatch.setattr(A, "y", 2, raising=False)
    assert A.y == 2
    monkeypatch.undo()
    assert not hasattr(A, "y")

    monkeypatch = MonkeyPatch()
    monkeypatch.setattr(A, "x", 2)
    assert A.x == 2
    monkeypatch.setattr(A, "x", 3)
    assert A.x == 3
    monkeypatch.undo()
    assert A.x == 1

    A.x = 5
    monkeypatch.undo()  # double-undo makes no modification
    assert A.x == 5


class TestSetattrWithImportPath:
    def test_string_expression(self, monkeypatch):
        monkeypatch.setattr("os.path.abspath", lambda x: "hello2")
        assert os.path.abspath("123") == "hello2"

    def test_string_expression_class(self, monkeypatch):
        monkeypatch.setattr("_pytest.config.Config", 42)
        import _pytest

        assert _pytest.config.Config == 42

    def test_unicode_string(self, monkeypatch):
        """
        Monkeypatch a configuration attribute in the _pytest module.
        
        This function temporarily replaces the `Config` attribute in the `_pytest.config` module with the integer value 42. After the test, the original attribute is restored. This is useful for testing how the system behaves when a specific configuration attribute is set to a different value.
        
        Parameters:
        monkeypatch (pytest.MonkeyPatch): A pytest fixture used to temporarily modify the system.
        
        Returns:
        None: This function does not return any value.
        """

        monkeypatch.setattr("_pytest.config.Config", 42)
        import _pytest

        assert _pytest.config.Config == 42
        monkeypatch.delattr("_pytest.config.Config")

    def test_wrong_target(self, monkeypatch):
        pytest.raises(TypeError, lambda: monkeypatch.setattr(None, None))

    def test_unknown_import(self, monkeypatch):
        pytest.raises(ImportError, lambda: monkeypatch.setattr("unkn123.classx", None))

    def test_unknown_attr(self, monkeypatch):
        pytest.raises(
            AttributeError, lambda: monkeypatch.setattr("os.path.qweqwe", None)
        )

    def test_unknown_attr_non_raising(self, monkeypatch):
        # https://github.com/pytest-dev/pytest/issues/746
        monkeypatch.setattr("os.path.qweqwe", 42, raising=False)
        assert os.path.qweqwe == 42

    def test_delattr(self, monkeypatch):
        monkeypatch.delattr("os.path.abspath")
        assert not hasattr(os.path, "abspath")
        monkeypatch.undo()
        assert os.path.abspath


def test_delattr():
    """
    Monkeypatch an object to delete an attribute.
    
    This function demonstrates how to use the `MonkeyPatch` context manager to delete an attribute from a class. It also shows how to handle cases where the attribute does not exist and how to revert the changes.
    
    Parameters:
    A (class): The class from which the attribute will be deleted.
    name (str): The name of the attribute to delete.
    
    Returns:
    None: The function does not return any value. It modifies the class in place.
    """

    class A:
        x = 1

    monkeypatch = MonkeyPatch()
    monkeypatch.delattr(A, "x")
    assert not hasattr(A, "x")
    monkeypatch.undo()
    assert A.x == 1

    monkeypatch = MonkeyPatch()
    monkeypatch.delattr(A, "x")
    pytest.raises(AttributeError, monkeypatch.delattr, A, "y")
    monkeypatch.delattr(A, "y", raising=False)
    monkeypatch.setattr(A, "x", 5, raising=False)
    assert A.x == 5
    monkeypatch.undo()
    assert A.x == 1


def test_setitem():
    d = {"x": 1}
    monkeypatch = MonkeyPatch()
    monkeypatch.setitem(d, "x", 2)
    monkeypatch.setitem(d, "y", 1700)
    monkeypatch.setitem(d, "y", 1700)
    assert d["x"] == 2
    assert d["y"] == 1700
    monkeypatch.setitem(d, "x", 3)
    assert d["x"] == 3
    monkeypatch.undo()
    assert d["x"] == 1
    assert "y" not in d
    d["x"] = 5
    monkeypatch.undo()
    assert d["x"] == 5


def test_setitem_deleted_meanwhile():
    """
    Monkeypatch a dictionary to set an item and then delete it. The function uses the MonkeyPatch fixture to temporarily set an item in the dictionary and then delete it. The MonkeyPatch fixture is then reverted to its original state.
    
    Parameters:
    None
    
    Returns:
    None
    
    Note:
    - The dictionary `d` is modified within the function.
    - The `MonkeyPatch` fixture is used to temporarily modify the dictionary.
    - The function asserts that the dictionary is empty after the MonkeyPatch
    """

    d = {}
    monkeypatch = MonkeyPatch()
    monkeypatch.setitem(d, "x", 2)
    del d["x"]
    monkeypatch.undo()
    assert not d


@pytest.mark.parametrize("before", [True, False])
def test_setenv_deleted_meanwhile(before):
    key = "qwpeoip123"
    if before:
        os.environ[key] = "world"
    monkeypatch = MonkeyPatch()
    monkeypatch.setenv(key, "hello")
    del os.environ[key]
    monkeypatch.undo()
    if before:
        assert os.environ[key] == "world"
        del os.environ[key]
    else:
        assert key not in os.environ


def test_delitem():
    d = {"x": 1}
    monkeypatch = MonkeyPatch()
    monkeypatch.delitem(d, "x")
    assert "x" not in d
    monkeypatch.delitem(d, "y", raising=False)
    pytest.raises(KeyError, monkeypatch.delitem, d, "y")
    assert not d
    monkeypatch.setitem(d, "y", 1700)
    assert d["y"] == 1700
    d["hello"] = "world"
    monkeypatch.setitem(d, "x", 1500)
    assert d["x"] == 1500
    monkeypatch.undo()
    assert d == {"hello": "world", "x": 1}


def test_setenv():
    """
    Monkeypatch the environment to set a variable and then undo the change.
    
    This function uses the `pytest.MonkeyPatch` object to set an environment variable
    and then undo the change after the test.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - A warning is issued during the test.
    - The environment variable 'XYZ123' is set to '2'.
    - The variable is then removed from the environment after the test.
    - This function is intended for
    """

    monkeypatch = MonkeyPatch()
    with pytest.warns(pytest.PytestWarning):
        monkeypatch.setenv("XYZ123", 2)
    import os

    assert os.environ["XYZ123"] == "2"
    monkeypatch.undo()
    assert "XYZ123" not in os.environ


def test_delenv():
    name = "xyz1234"
    assert name not in os.environ
    monkeypatch = MonkeyPatch()
    pytest.raises(KeyError, monkeypatch.delenv, name, raising=True)
    monkeypatch.delenv(name, raising=False)
    monkeypatch.undo()
    os.environ[name] = "1"
    try:
        monkeypatch = MonkeyPatch()
        monkeypatch.delenv(name)
        assert name not in os.environ
        monkeypatch.setenv(name, "3")
        assert os.environ[name] == "3"
        monkeypatch.undo()
        assert os.environ[name] == "1"
    finally:
        if name in os.environ:
            del os.environ[name]


class TestEnvironWarnings:
    """
    os.environ keys and values should be native strings, otherwise it will cause problems with other modules (notably
    subprocess). On Python 2 os.environ accepts anything without complaining, while Python 3 does the right thing
    and raises an error.
    """

    VAR_NAME = "PYTEST_INTERNAL_MY_VAR"

    def test_setenv_non_str_warning(self, monkeypatch):
        value = 2
        msg = (
            "Value of environment variable PYTEST_INTERNAL_MY_VAR type should be str, "
            "but got 2 (type: int); converted to str implicitly"
        )
        with pytest.warns(pytest.PytestWarning, match=re.escape(msg)):
            monkeypatch.setenv(str(self.VAR_NAME), value)


def test_setenv_prepend():
    import os

    monkeypatch = MonkeyPatch()
    with pytest.warns(pytest.PytestWarning):
        monkeypatch.setenv("XYZ123", 2, prepend="-")
    assert os.environ["XYZ123"] == "2"
    with pytest.warns(pytest.PytestWarning):
        monkeypatch.setenv("XYZ123", 3, prepend="-")
    assert os.environ["XYZ123"] == "3-2"
    monkeypatch.undo()
    assert "XYZ123" not in os.environ


def test_monkeypatch_plugin(testdir):
    reprec = testdir.inline_runsource(
        """
        def test_method(monkeypatch):
            assert monkeypatch.__class__.__name__ == "MonkeyPatch"
    """
    )
    res = reprec.countoutcomes()
    assert tuple(res) == (1, 0, 0), res


def test_syspath_prepend(mp):
    """
    Prepend paths to the system path and then undo the changes.
    
    This function uses the `pytest-monkeypatch` fixture to manipulate the system path (`sys.path`).
    It first saves the current state of `sys.path`, then prepends two paths ("hello" and "world") to the beginning of `sys.path`.
    Afterwards, it checks that the paths have been correctly prepended and then undoes the changes, restoring `sys.path` to its original state.
    
    Parameters:
    - mp (
    """

    old = list(sys.path)
    mp.syspath_prepend("world")
    mp.syspath_prepend("hello")
    assert sys.path[0] == "hello"
    assert sys.path[1] == "world"
    mp.undo()
    assert sys.path == old
    mp.undo()
    assert sys.path == old


def test_syspath_prepend_double_undo(mp):
    old_syspath = sys.path[:]
    try:
        mp.syspath_prepend("hello world")
        mp.undo()
        sys.path.append("more hello world")
        mp.undo()
        assert sys.path[-1] == "more hello world"
    finally:
        sys.path[:] = old_syspath


def test_chdir_with_path_local(mp, tmpdir):
    mp.chdir(tmpdir)
    assert os.getcwd() == tmpdir.strpath


def test_chdir_with_str(mp, tmpdir):
    mp.chdir(tmpdir.strpath)
    assert os.getcwd() == tmpdir.strpath


def test_chdir_undo(mp, tmpdir):
    cwd = os.getcwd()
    mp.chdir(tmpdir)
    mp.undo()
    assert os.getcwd() == cwd


def test_chdir_double_undo(mp, tmpdir):
    mp.chdir(tmpdir.strpath)
    mp.undo()
    tmpdir.chdir()
    mp.undo()
    assert os.getcwd() == tmpdir.strpath


def test_issue185_time_breaks(testdir):
    """
    Tests the function `test_issue185_time_breaks` which creates a test scenario where the `time` module's `time` function is monkeypatched to raise an exception. The test verifies that the monkeypatching does not break the test execution and that the test still passes.
    
    Parameters:
    - testdir: Pytest test directory object used to create and run tests.
    
    Returns:
    - result: The result of the pytest run, indicating whether the test passed or failed.
    """

    testdir.makepyfile(
        """
        import time
        def test_m(monkeypatch):
            def f():
                raise Exception
            monkeypatch.setattr(time, "time", f)
    """
    )
    result = testdir.runpytest()
    result.stdout.fnmatch_lines(
        """
        *1 passed*
    """
    )


def test_importerror(testdir):
    p = testdir.mkpydir("package")
    p.join("a.py").write(
        textwrap.dedent(
            """\
        import doesnotexist

        x = 1
    """
        )
    )
    testdir.tmpdir.join("test_importerror.py").write(
        textwrap.dedent(
            """\
        def test_importerror(monkeypatch):
            monkeypatch.setattr('package.a.x', 2)
    """
        )
    )
    result = testdir.runpytest()
    result.stdout.fnmatch_lines(
        """
        *import error in package.a: No module named 'doesnotexist'*
    """
    )


class SampleNew:
    @staticmethod
    def hello():
        return True


class SampleNewInherit(SampleNew):
    pass


class SampleOld:
    # oldstyle on python2
    @staticmethod
    def hello():
        return True


class SampleOldInherit(SampleOld):
    pass


@pytest.mark.parametrize(
    "Sample",
    [SampleNew, SampleNewInherit, SampleOld, SampleOldInherit],
    ids=["new", "new-inherit", "old", "old-inherit"],
)
def test_issue156_undo_staticmethod(Sample):
    monkeypatch = MonkeyPatch()

    monkeypatch.setattr(Sample, "hello", None)
    assert Sample.hello is None

    monkeypatch.undo()
    assert Sample.hello()


def test_undo_class_descriptors_delattr():
    """
    Unittest for the `delattr` functionality of the `MonkeyPatch` class.
    
    This function tests the ability of `MonkeyPatch` to delete class descriptors (classmethod and staticmethod) and then revert the changes.
    
    Parameters:
    - monkeypatch (MonkeyPatch): A fixture that provides access to the `MonkeyPatch` class for testing.
    
    The function creates a parent and child class with classmethod and staticmethod. It then uses `MonkeyPatch` to delete these methods from the parent class. After that
    """

    class SampleParent:
        @classmethod
        def hello(_cls):
            pass

        @staticmethod
        def world():
            pass

    class SampleChild(SampleParent):
        pass

    monkeypatch = MonkeyPatch()

    original_hello = SampleChild.hello
    original_world = SampleChild.world
    monkeypatch.delattr(SampleParent, "hello")
    monkeypatch.delattr(SampleParent, "world")
    assert getattr(SampleParent, "hello", None) is None
    assert getattr(SampleParent, "world", None) is None

    monkeypatch.undo()
    assert original_hello == SampleChild.hello
    assert original_world == SampleChild.world


def test_issue1338_name_resolving():
    pytest.importorskip("requests")
    monkeypatch = MonkeyPatch()
    try:
        monkeypatch.delattr("requests.sessions.Session.request")
    finally:
        monkeypatch.undo()


def test_context():
    monkeypatch = MonkeyPatch()

    import functools
    import inspect

    with monkeypatch.context() as m:
        m.setattr(functools, "partial", 3)
        assert not inspect.isclass(functools.partial)
    assert inspect.isclass(functools.partial)


def test_syspath_prepend_with_namespace_packages(testdir, monkeypatch):
    for dirname in "hello", "world":
        d = testdir.mkdir(dirname)
        ns = d.mkdir("ns_pkg")
        ns.join("__init__.py").write(
            "__import__('pkg_resources').declare_namespace(__name__)"
        )
        lib = ns.mkdir(dirname)
        lib.join("__init__.py").write("def check(): return %r" % dirname)

    monkeypatch.syspath_prepend("hello")
    import ns_pkg.hello

    assert ns_pkg.hello.check() == "hello"

    with pytest.raises(ImportError):
        import ns_pkg.world

    # Prepending should call fixup_namespace_packages.
    monkeypatch.syspath_prepend("world")
    import ns_pkg.world

    assert ns_pkg.world.check() == "world"

    # Should invalidate caches via importlib.invalidate_caches.
    tmpdir = testdir.tmpdir
    modules_tmpdir = tmpdir.mkdir("modules_tmpdir")
    monkeypatch.syspath_prepend(str(modules_tmpdir))
    modules_tmpdir.join("main_app.py").write("app = True")
    from main_app import app  # noqa: F401
