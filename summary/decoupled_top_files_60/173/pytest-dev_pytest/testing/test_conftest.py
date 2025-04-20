import textwrap

import py

import pytest
from _pytest.config import PytestPluginManager
from _pytest.main import ExitCode


def ConftestWithSetinitial(path):
    conftest = PytestPluginManager()
    conftest_setinitial(conftest, [path])
    return conftest


def conftest_setinitial(conftest, args, confcutdir=None):
    """
    Set initial configuration for conftest.
    
    This function initializes the configuration for a conftest based on the provided arguments.
    
    Parameters:
    conftest (object): The conftest object to initialize.
    args (str): The file or directory to be used for the conftest.
    confcutdir (str, optional): The directory for configuration cuts. Defaults to None.
    
    Returns:
    None: This function does not return any value. It modifies the conftest object in place
    """

    class Namespace:
        def __init__(self):
            """
            Initialize the object with the following parameters:
            - file_or_dir (str): The file or directory to be processed.
            - confcutdir (str): The directory for configuration cuts.
            - noconftest (bool, optional): If True, disables configuration tests. Default is False.
            - pyargs (bool, optional): If True, enables Python argument handling. Default is False.
            
            This function initializes the object with the provided arguments and sets up the necessary attributes for further processing.
            """

            self.file_or_dir = args
            self.confcutdir = str(confcutdir)
            self.noconftest = False
            self.pyargs = False

    conftest._set_initial_conftests(Namespace())


@pytest.mark.usefixtures("_sys_snapshot")
class TestConftestValueAccessGlobal:
    @pytest.fixture(scope="module", params=["global", "inpackage"])
    def basedir(self, request, tmpdir_factory):
        """
        Generates a temporary directory structure for testing purposes.
        
        This function creates a temporary directory with a specified structure and files. The directory structure includes a base directory with subdirectories and conftest.py files. The function accepts a request parameter to determine if the package structure should be included.
        
        Parameters:
        request (pytest.FixtureRequest): The pytest request object used to parametrize the test.
        tmpdir_factory (pytest.TempPathFactory): The pytest temporary directory factory used to create the temporary directory.
        
        Y
        """

        tmpdir = tmpdir_factory.mktemp("basedir", numbered=True)
        tmpdir.ensure("adir/conftest.py").write("a=1 ; Directory = 3")
        tmpdir.ensure("adir/b/conftest.py").write("b=2 ; a = 1.5")
        if request.param == "inpackage":
            tmpdir.ensure("adir/__init__.py")
            tmpdir.ensure("adir/b/__init__.py")

        yield tmpdir

    def test_basic_init(self, basedir):
        """
        Initialize the PytestPluginManager with a given base directory.
        
        This method initializes the PytestPluginManager and sets up a directory structure for testing purposes.
        
        Parameters:
        basedir (Path): The base directory where the test directory structure will be created.
        
        Returns:
        None: This method does not return any value. It sets up the necessary directory and configuration for subsequent tests.
        
        Example:
        >>> basedir = Path("/tmp/testdir")
        >>> conftest = PytestPluginManager()
        """

        conftest = PytestPluginManager()
        p = basedir.join("adir")
        assert conftest._rget_with_confmod("a", p)[1] == 1

    def test_immediate_initialiation_and_incremental_are_the_same(self, basedir):
        conftest = PytestPluginManager()
        assert not len(conftest._dirpath2confmods)
        conftest._getconftestmodules(basedir)
        snap1 = len(conftest._dirpath2confmods)
        assert snap1 == 1
        conftest._getconftestmodules(basedir.join("adir"))
        assert len(conftest._dirpath2confmods) == snap1 + 1
        conftest._getconftestmodules(basedir.join("b"))
        assert len(conftest._dirpath2confmods) == snap1 + 2

    def test_value_access_not_existing(self, basedir):
        conftest = ConftestWithSetinitial(basedir)
        with pytest.raises(KeyError):
            conftest._rget_with_confmod("a", basedir)

    def test_value_access_by_path(self, basedir):
        conftest = ConftestWithSetinitial(basedir)
        adir = basedir.join("adir")
        assert conftest._rget_with_confmod("a", adir)[1] == 1
        assert conftest._rget_with_confmod("a", adir.join("b"))[1] == 1.5

    def test_value_access_with_confmod(self, basedir):
        """
        Tests the value access with configuration modification in a specified directory.
        
        This function checks the retrieval of a configuration value and the associated module path when using the `_rget_with_confmod` method of a `ConftestWithSetinitial` object. The test is performed in a specified directory structure.
        
        Parameters:
        basedir (py.path.local): The base directory for the test, which includes a subdirectory structure.
        
        Returns:
        None: This function asserts conditions rather than returning a value.
        
        Key Steps
        """

        startdir = basedir.join("adir", "b")
        startdir.ensure("xx", dir=True)
        conftest = ConftestWithSetinitial(startdir)
        mod, value = conftest._rget_with_confmod("a", startdir)
        assert value == 1.5
        path = py.path.local(mod.__file__)
        assert path.dirpath() == basedir.join("adir", "b")
        assert path.purebasename.startswith("conftest")


def test_conftest_in_nonpkg_with_init(tmpdir, _sys_snapshot):
    tmpdir.ensure("adir-1.0/conftest.py").write("a=1 ; Directory = 3")
    tmpdir.ensure("adir-1.0/b/conftest.py").write("b=2 ; a = 1.5")
    tmpdir.ensure("adir-1.0/b/__init__.py")
    tmpdir.ensure("adir-1.0/__init__.py")
    ConftestWithSetinitial(tmpdir.join("adir-1.0", "b"))


def test_doubledash_considered(testdir):
    conf = testdir.mkdir("--option")
    conf.ensure("conftest.py")
    conftest = PytestPluginManager()
    conftest_setinitial(conftest, [conf.basename, conf.basename])
    values = conftest._getconftestmodules(conf)
    assert len(values) == 1


def test_issue151_load_all_conftests(testdir):
    names = "code proj src".split()
    for name in names:
        p = testdir.mkdir(name)
        p.ensure("conftest.py")

    conftest = PytestPluginManager()
    conftest_setinitial(conftest, names)
    d = list(conftest._conftestpath2mod.values())
    assert len(d) == len(names)


def test_conftest_global_import(testdir):
    testdir.makeconftest("x=3")
    p = testdir.makepyfile(
        """
        import py, pytest
        from _pytest.config import PytestPluginManager
        conf = PytestPluginManager()
        mod = conf._importconftest(py.path.local("conftest.py"))
        assert mod.x == 3
        import conftest
        assert conftest is mod, (conftest, mod)
        subconf = py.path.local().ensure("sub", "conftest.py")
        subconf.write("y=4")
        mod2 = conf._importconftest(subconf)
        assert mod != mod2
        assert mod2.y == 4
        import conftest
        assert conftest is mod2, (conftest, mod)
    """
    )
    res = testdir.runpython(p)
    assert res.ret == 0


def test_conftestcutdir(testdir):
    conf = testdir.makeconftest("")
    p = testdir.mkdir("x")
    conftest = PytestPluginManager()
    conftest_setinitial(conftest, [testdir.tmpdir], confcutdir=p)
    values = conftest._getconftestmodules(p)
    assert len(values) == 0
    values = conftest._getconftestmodules(conf.dirpath())
    assert len(values) == 0
    assert conf not in conftest._conftestpath2mod
    # but we can still import a conftest directly
    conftest._importconftest(conf)
    values = conftest._getconftestmodules(conf.dirpath())
    assert values[0].__file__.startswith(str(conf))
    # and all sub paths get updated properly
    values = conftest._getconftestmodules(p)
    assert len(values) == 1
    assert values[0].__file__.startswith(str(conf))


def test_conftestcutdir_inplace_considered(testdir):
    conf = testdir.makeconftest("")
    conftest = PytestPluginManager()
    conftest_setinitial(conftest, [conf.dirpath()], confcutdir=conf.dirpath())
    values = conftest._getconftestmodules(conf.dirpath())
    assert len(values) == 1
    assert values[0].__file__.startswith(str(conf))


@pytest.mark.parametrize("name", "test tests whatever .dotdir".split())
def test_setinitial_conftest_subdirs(testdir, name):
    sub = testdir.mkdir(name)
    subconftest = sub.ensure("conftest.py")
    conftest = PytestPluginManager()
    conftest_setinitial(conftest, [sub.dirpath()], confcutdir=testdir.tmpdir)
    if name not in ("whatever", ".dotdir"):
        assert subconftest in conftest._conftestpath2mod
        assert len(conftest._conftestpath2mod) == 1
    else:
        assert subconftest not in conftest._conftestpath2mod
        assert len(conftest._conftestpath2mod) == 0


def test_conftest_confcutdir(testdir):
    """
    Test the pytest configuration and directory cutting feature.
    
    This function tests the pytest configuration and directory cutting feature by creating a temporary conftest file and a subdirectory with its own conftest file. The function then runs pytest with the specified configuration and checks for the presence of the `--xyz` option in the help output.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest test directory fixture that provides methods to create and manipulate test files and directories.
    
    Returns:
    - None: The function asserts
    """

    testdir.makeconftest("assert 0")
    x = testdir.mkdir("x")
    x.join("conftest.py").write(
        textwrap.dedent(
            """\
            def pytest_addoption(parser):
                parser.addoption("--xyz", action="store_true")
            """
        )
    )
    result = testdir.runpytest("-h", "--confcutdir=%s" % x, x)
    result.stdout.fnmatch_lines(["*--xyz*"])
    assert "warning: could not load initial" not in result.stdout.str()


@pytest.mark.skipif(
    not hasattr(py.path.local, "mksymlinkto"),
    reason="symlink not available on this platform",
)
def test_conftest_symlink(testdir):
    """Ensure that conftest.py is used for resolved symlinks."""
    real = testdir.tmpdir.mkdir("real")
    realtests = real.mkdir("app").mkdir("tests")
    testdir.tmpdir.join("symlinktests").mksymlinkto(realtests)
    testdir.tmpdir.join("symlink").mksymlinkto(real)
    testdir.makepyfile(
        **{
            "real/app/tests/test_foo.py": "def test1(fixture): pass",
            "real/conftest.py": textwrap.dedent(
                """
                import pytest

                print("conftest_loaded")

                @pytest.fixture
                def fixture():
                    print("fixture_used")
                """
            ),
        }
    )
    result = testdir.runpytest("-vs", "symlinktests")
    result.stdout.fnmatch_lines(
        [
            "*conftest_loaded*",
            "real/app/tests/test_foo.py::test1 fixture_used",
            "PASSED",
        ]
    )
    assert result.ret == ExitCode.OK

    # Should not cause "ValueError: Plugin already registered" (#4174).
    result = testdir.runpytest("-vs", "symlink")
    assert result.ret == ExitCode.OK

    realtests.ensure("__init__.py")
    result = testdir.runpytest("-vs", "symlinktests/test_foo.py::test1")
    result.stdout.fnmatch_lines(
        [
            "*conftest_loaded*",
            "real/app/tests/test_foo.py::test1 fixture_used",
            "PASSED",
        ]
    )
    assert result.ret == ExitCode.OK


@pytest.mark.skipif(
    not hasattr(py.path.local, "mksymlinkto"),
    reason="symlink not available on this platform",
)
def test_conftest_symlink_files(testdir):
    """Check conftest.py loading when running in directory with symlinks."""
    real = testdir.tmpdir.mkdir("real")
    source = {
        "app/test_foo.py": "def test1(fixture): pass",
        "app/__init__.py": "",
        "app/conftest.py": textwrap.dedent(
            """
            import pytest

            print("conftest_loaded")

            @pytest.fixture
            def fixture():
                print("fixture_used")
            """
        ),
    }
    testdir.makepyfile(**{"real/%s" % k: v for k, v in source.items()})

    # Create a build directory that contains symlinks to actual files
    # but doesn't symlink actual directories.
    build = testdir.tmpdir.mkdir("build")
    build.mkdir("app")
    for f in source:
        build.join(f).mksymlinkto(real.join(f))
    build.chdir()
    result = testdir.runpytest("-vs", "app/test_foo.py")
    result.stdout.fnmatch_lines(["*conftest_loaded*", "PASSED"])
    assert result.ret == ExitCode.OK


def test_no_conftest(testdir):
    testdir.makeconftest("assert 0")
    result = testdir.runpytest("--noconftest")
    assert result.ret == ExitCode.NO_TESTS_COLLECTED

    result = testdir.runpytest()
    assert result.ret == ExitCode.USAGE_ERROR


def test_conftest_existing_resultlog(testdir):
    """
    Tests the pytest configuration with an existing result log file.
    
    This function runs pytest with the specified options and checks if the output includes the help message for the `--xyz` option. It creates a directory named 'tests' and a file named 'conftest.py' within it. The 'conftest.py' file adds a command-line option `--xyz`. It also creates an empty result log file named 'result.log'. The function then runs pytest with the `-h`, `--result
    """

    x = testdir.mkdir("tests")
    x.join("conftest.py").write(
        textwrap.dedent(
            """\
            def pytest_addoption(parser):
                parser.addoption("--xyz", action="store_true")
            """
        )
    )
    testdir.makefile(ext=".log", result="")  # Writes result.log
    result = testdir.runpytest("-h", "--resultlog", "result.log")
    result.stdout.fnmatch_lines(["*--xyz*"])


def test_conftest_existing_junitxml(testdir):
    x = testdir.mkdir("tests")
    x.join("conftest.py").write(
        textwrap.dedent(
            """\
            def pytest_addoption(parser):
                parser.addoption("--xyz", action="store_true")
            """
        )
    )
    testdir.makefile(ext=".xml", junit="")  # Writes junit.xml
    result = testdir.runpytest("-h", "--junitxml", "junit.xml")
    result.stdout.fnmatch_lines(["*--xyz*"])


def test_conftest_import_order(testdir, monkeypatch):
    ct1 = testdir.makeconftest("")
    sub = testdir.mkdir("sub")
    ct2 = sub.join("conftest.py")
    ct2.write("")

    def impct(p):
        return p

    conftest = PytestPluginManager()
    conftest._confcutdir = testdir.tmpdir
    monkeypatch.setattr(conftest, "_importconftest", impct)
    assert conftest._getconftestmodules(sub) == [ct1, ct2]


def test_fixture_dependency(testdir, monkeypatch):
    """
    This function runs a pytest with a specific configuration to test fixture dependencies. It creates a temporary directory structure with conftest and test files to define and use fixtures. The function ensures that unnecessary fixtures are not called and verifies that the correct fixture is used in a test.
    
    Parameters:
    - testdir: The pytest test directory object used to create and run tests.
    - monkeypatch: The pytest monkeypatch object used to modify the environment for testing.
    
    Returns:
    - A pytest result object indicating the outcome of
    """

    ct1 = testdir.makeconftest("")
    ct1 = testdir.makepyfile("__init__.py")
    ct1.write("")
    sub = testdir.mkdir("sub")
    sub.join("__init__.py").write("")
    sub.join("conftest.py").write(
        textwrap.dedent(
            """\
            import pytest

            @pytest.fixture
            def not_needed():
                assert False, "Should not be called!"

            @pytest.fixture
            def foo():
                assert False, "Should not be called!"

            @pytest.fixture
            def bar(foo):
                return 'bar'
            """
        )
    )
    subsub = sub.mkdir("subsub")
    subsub.join("__init__.py").write("")
    subsub.join("test_bar.py").write(
        textwrap.dedent(
            """\
            import pytest

            @pytest.fixture
            def bar():
                return 'sub bar'

            def test_event_fixture(bar):
                assert bar == 'sub bar'
            """
        )
    )
    result = testdir.runpytest("sub")
    result.stdout.fnmatch_lines(["*1 passed*"])


def test_conftest_found_with_double_dash(testdir):
    sub = testdir.mkdir("sub")
    sub.join("conftest.py").write(
        textwrap.dedent(
            """\
            def pytest_addoption(parser):
                parser.addoption("--hello-world", action="store_true")
            """
        )
    )
    p = sub.join("test_hello.py")
    p.write("def test_hello(): pass")
    result = testdir.runpytest(str(p) + "::test_hello", "-h")
    result.stdout.fnmatch_lines(
        """
        *--hello-world*
    """
    )


class TestConftestVisibility:
    def _setup_tree(self, testdir):  # for issue616
        """
        Setup a test directory structure for testing pytest fixture inheritance.
        
        This function creates a directory structure with multiple levels of packages and subpackages, each containing test files and conftest files. The structure is designed to test how pytest handles fixture inheritance across different levels of the directory tree.
        
        Parameters:
        testdir (pytest.Testdir): The temporary directory object provided by pytest for testing.
        
        Returns:
        dict: A dictionary containing paths to different parts of the created directory structure:
        - 'runner': The path
        """

        # example mostly taken from:
        # https://mail.python.org/pipermail/pytest-dev/2014-September/002617.html
        runner = testdir.mkdir("empty")
        package = testdir.mkdir("package")

        package.join("conftest.py").write(
            textwrap.dedent(
                """\
                import pytest
                @pytest.fixture
                def fxtr():
                    return "from-package"
                """
            )
        )
        package.join("test_pkgroot.py").write(
            textwrap.dedent(
                """\
                def test_pkgroot(fxtr):
                    assert fxtr == "from-package"
                """
            )
        )

        swc = package.mkdir("swc")
        swc.join("__init__.py").ensure()
        swc.join("conftest.py").write(
            textwrap.dedent(
                """\
                import pytest
                @pytest.fixture
                def fxtr():
                    return "from-swc"
                """
            )
        )
        swc.join("test_with_conftest.py").write(
            textwrap.dedent(
                """\
                def test_with_conftest(fxtr):
                    assert fxtr == "from-swc"
                """
            )
        )

        snc = package.mkdir("snc")
        snc.join("__init__.py").ensure()
        snc.join("test_no_conftest.py").write(
            textwrap.dedent(
                """\
                def test_no_conftest(fxtr):
                    assert fxtr == "from-package"   # No local conftest.py, so should
                                                    # use value from parent dir's
                """
            )
        )
        print("created directory structure:")
        for x in testdir.tmpdir.visit():
            print("   " + x.relto(testdir.tmpdir))

        return {"runner": runner, "package": package, "swc": swc, "snc": snc}

    # N.B.: "swc" stands for "subdir with conftest.py"
    #       "snc" stands for "subdir no [i.e. without] conftest.py"
    @pytest.mark.parametrize(
        "chdir,testarg,expect_ntests_passed",
        [
            # Effective target: package/..
            ("runner", "..", 3),
            ("package", "..", 3),
            ("swc", "../..", 3),
            ("snc", "../..", 3),
            # Effective target: package
            ("runner", "../package", 3),
            ("package", ".", 3),
            ("swc", "..", 3),
            ("snc", "..", 3),
            # Effective target: package/swc
            ("runner", "../package/swc", 1),
            ("package", "./swc", 1),
            ("swc", ".", 1),
            ("snc", "../swc", 1),
            # Effective target: package/snc
            ("runner", "../package/snc", 1),
            ("package", "./snc", 1),
            ("swc", "../snc", 1),
            ("snc", ".", 1),
        ],
    )
    def test_parsefactories_relative_node_ids(
        self, testdir, chdir, testarg, expect_ntests_passed
    ):
        """#616"""
        dirs = self._setup_tree(testdir)
        print("pytest run in cwd: %s" % (dirs[chdir].relto(testdir.tmpdir)))
        print("pytestarg        : %s" % (testarg))
        print("expected pass    : %s" % (expect_ntests_passed))
        with dirs[chdir].as_cwd():
            reprec = testdir.inline_run(testarg, "-q", "--traceconfig")
            reprec.assertoutcome(passed=expect_ntests_passed)


@pytest.mark.parametrize(
    "confcutdir,passed,error", [(".", 2, 0), ("src", 1, 1), (None, 1, 1)]
)
def test_search_conftest_up_to_inifile(testdir, confcutdir, passed, error):
    """Test that conftest files are detected only up to an ini file, unless
    an explicit --confcutdir option is given.
    """
    root = testdir.tmpdir
    src = root.join("src").ensure(dir=1)
    src.join("pytest.ini").write("[pytest]")
    src.join("conftest.py").write(
        textwrap.dedent(
            """\
            import pytest
            @pytest.fixture
            def fix1(): pass
            """
        )
    )
    src.join("test_foo.py").write(
        textwrap.dedent(
            """\
            def test_1(fix1):
                pass
            def test_2(out_of_reach):
                pass
            """
        )
    )
    root.join("conftest.py").write(
        textwrap.dedent(
            """\
            import pytest
            @pytest.fixture
            def out_of_reach(): pass
            """
        )
    )

    args = [str(src)]
    if confcutdir:
        args = ["--confcutdir=%s" % root.join(confcutdir)]
    result = testdir.runpytest(*args)
    match = ""
    if passed:
        match += "*%d passed*" % passed
    if error:
        match += "*%d error*" % error
    result.stdout.fnmatch_lines(match)


def test_issue1073_conftest_special_objects(testdir):
    testdir.makeconftest(
        """\
        class DontTouchMe(object):
            def __getattr__(self, x):
                raise Exception('cant touch me')

        x = DontTouchMe()
        """
    )
    testdir.makepyfile(
        """\
        def test_some():
            pass
        """
    )
    res = testdir.runpytest()
    assert res.ret == 0


def test_conftest_exception_handling(testdir):
    testdir.makeconftest(
        """\
        raise ValueError()
        """
    )
    testdir.makepyfile(
        """\
        def test_some():
            pass
        """
    )
    res = testdir.runpytest()
    assert res.ret == 4
    assert "raise ValueError()" in [line.strip() for line in res.errlines]


def test_hook_proxy(testdir):
    """Session's gethookproxy() would cache conftests incorrectly (#2016).
    It was decided to remove the cache altogether.
    """
    testdir.makepyfile(
        **{
            "root/demo-0/test_foo1.py": "def test1(): pass",
            "root/demo-a/test_foo2.py": "def test1(): pass",
            "root/demo-a/conftest.py": """\
            def pytest_ignore_collect(path, config):
                return True
            """,
            "root/demo-b/test_foo3.py": "def test1(): pass",
            "root/demo-c/test_foo4.py": "def test1(): pass",
        }
    )
    result = testdir.runpytest()
    result.stdout.fnmatch_lines(
        ["*test_foo1.py*", "*test_foo3.py*", "*test_foo4.py*", "*3 passed*"]
    )


def test_required_option_help(testdir):
    testdir.makeconftest("assert 0")
    x = testdir.mkdir("x")
    x.join("conftest.py").write(
        textwrap.dedent(
            """\
            def pytest_addoption(parser):
                parser.addoption("--xyz", action="store_true", required=True)
            """
        )
    )
    result = testdir.runpytest("-h", x)
    assert "argument --xyz is required" not in result.stdout.str()
    assert "general:" in result.stdout.str()
