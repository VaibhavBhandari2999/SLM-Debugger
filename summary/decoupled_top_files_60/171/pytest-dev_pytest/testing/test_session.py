from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pytest
from _pytest.main import EXIT_NOTESTSCOLLECTED


class SessionTests(object):
    def test_basic_testitem_events(self, testdir):
        """
        Tests the basic test item events in a test suite.
        
        This function runs a test suite defined in a temporary file and verifies the outcomes of the test items. The test suite includes various test cases and a test class. The function checks the number of passed, skipped, and failed test items and ensures that the failed items are correctly identified. It also verifies that the test items are collected as expected.
        
        Parameters:
        testdir (pytest.Testdir): A pytest test directory fixture used to create and run test
        """

        tfile = testdir.makepyfile(
            """
            def test_one():
                pass
            def test_one_one():
                assert 0
            def test_other():
                raise ValueError(23)
            class TestClass(object):
                def test_two(self, someargs):
                    pass
        """
        )
        reprec = testdir.inline_run(tfile)
        passed, skipped, failed = reprec.listoutcomes()
        assert len(skipped) == 0
        assert len(passed) == 1
        assert len(failed) == 3

        def end(x):
            return x.nodeid.split("::")[-1]

        assert end(failed[0]) == "test_one_one"
        assert end(failed[1]) == "test_other"
        itemstarted = reprec.getcalls("pytest_itemcollected")
        assert len(itemstarted) == 4
        # XXX check for failing funcarg setup
        # colreports = reprec.getcalls("pytest_collectreport")
        # assert len(colreports) == 4
        # assert colreports[1].report.failed

    def test_nested_import_error(self, testdir):
        tfile = testdir.makepyfile(
            """
            import import_fails
            def test_this():
                assert import_fails.a == 1
        """,
            import_fails="""
            import does_not_work
            a = 1
        """,
        )
        reprec = testdir.inline_run(tfile)
        values = reprec.getfailedcollections()
        assert len(values) == 1
        out = str(values[0].longrepr)
        assert out.find("does_not_work") != -1

    def test_raises_output(self, testdir):
        reprec = testdir.inline_runsource(
            """
            import pytest
            def test_raises_doesnt():
                pytest.raises(ValueError, int, "3")
        """
        )
        passed, skipped, failed = reprec.listoutcomes()
        assert len(failed) == 1
        out = failed[0].longrepr.reprcrash.message
        assert "DID NOT RAISE" in out

    def test_syntax_error_module(self, testdir):
        """
        Tests the behavior of the `test_syntax_error_module` function in the given test framework.
        
        This function runs a source code that is not valid Python and checks if the test framework correctly identifies it as a syntax error.
        
        Parameters:
        testdir (pytest.Testdir): The test directory object used to run the source code.
        
        Returns:
        None: This function does not return anything. It asserts that the test framework correctly identifies the source code as a syntax error.
        """

        reprec = testdir.inline_runsource("this is really not python")
        values = reprec.getfailedcollections()
        assert len(values) == 1
        out = str(values[0].longrepr)
        assert out.find(str("not python")) != -1

    def test_exit_first_problem(self, testdir):
        reprec = testdir.inline_runsource(
            """
            def test_one(): assert 0
            def test_two(): assert 0
        """,
            "--exitfirst",
        )
        passed, skipped, failed = reprec.countoutcomes()
        assert failed == 1
        assert passed == skipped == 0

    def test_maxfail(self, testdir):
        reprec = testdir.inline_runsource(
            """
            def test_one(): assert 0
            def test_two(): assert 0
            def test_three(): assert 0
        """,
            "--maxfail=2",
        )
        passed, skipped, failed = reprec.countoutcomes()
        assert failed == 2
        assert passed == skipped == 0

    def test_broken_repr(self, testdir):
        """
        Tests the behavior of a class with a broken __repr__ method.
        
        This function runs a test suite to check how pytest handles a class with a broken __repr__ method. The class `BrokenRepr1` is defined with a `foo` attribute and a `__repr__` method that raises an exception. Two test methods are included: `test_explicit_bad_repr` and `test_implicit_bad_repr1`. The first test explicitly checks the exception raised by the `__repr__
        """

        p = testdir.makepyfile(
            """
            import pytest
            class BrokenRepr1(object):
                foo=0
                def __repr__(self):
                    raise Exception("Ha Ha fooled you, I'm a broken repr().")

            class TestBrokenClass(object):
                def test_explicit_bad_repr(self):
                    t = BrokenRepr1()
                    with pytest.raises(Exception, match="I'm a broken repr"):
                        repr(t)

                def test_implicit_bad_repr1(self):
                    t = BrokenRepr1()
                    assert t.foo == 1

        """
        )
        reprec = testdir.inline_run(p)
        passed, skipped, failed = reprec.listoutcomes()
        assert (len(passed), len(skipped), len(failed)) == (1, 0, 1)
        out = failed[0].longrepr.reprcrash.message
        assert (
            out.find(
                """[Exception("Ha Ha fooled you, I'm a broken repr().") raised in repr()]"""
            )
            != -1
        )

    def test_broken_repr_with_showlocals_verbose(self, testdir):
        """
        Test the behavior of the test_broken_repr_with_showlocals_verbose function.
        
        This function runs a test case where an object with a broken `__repr__` method is used in an assertion. The test case is expected to fail due to the error in the `__repr__` method. The function checks that the traceback and local variables are correctly displayed, including the error raised in the `__repr__` method.
        
        Parameters:
        testdir (pytest.Testdir): A pytest Testdir object
        """

        p = testdir.makepyfile(
            """
            class ObjWithErrorInRepr:
                def __repr__(self):
                    raise NotImplementedError

            def test_repr_error():
                x = ObjWithErrorInRepr()
                assert x == "value"
        """
        )
        reprec = testdir.inline_run("--showlocals", "-vv", p)
        passed, skipped, failed = reprec.listoutcomes()
        assert (len(passed), len(skipped), len(failed)) == (0, 0, 1)
        entries = failed[0].longrepr.reprtraceback.reprentries
        assert len(entries) == 1
        repr_locals = entries[0].reprlocals
        assert repr_locals.lines
        assert len(repr_locals.lines) == 1
        assert repr_locals.lines[0].startswith(
            'x          = <[NotImplementedError("") raised in repr()] ObjWithErrorInRepr'
        )

    def test_skip_file_by_conftest(self, testdir):
        testdir.makepyfile(
            conftest="""
            import pytest
            def pytest_collect_file():
                pytest.skip("intentional")
        """,
            test_file="""
            def test_one(): pass
        """,
        )
        try:
            reprec = testdir.inline_run(testdir.tmpdir)
        except pytest.skip.Exception:  # pragma: no covers
            pytest.fail("wrong skipped caught")
        reports = reprec.getreports("pytest_collectreport")
        assert len(reports) == 1
        assert reports[0].skipped


class TestNewSession(SessionTests):
    def test_order_of_execution(self, testdir):
        reprec = testdir.inline_runsource(
            """
            values = []
            def test_1():
                values.append(1)
            def test_2():
                values.append(2)
            def test_3():
                assert values == [1,2]
            class Testmygroup(object):
                reslist = values
                def test_1(self):
                    self.reslist.append(1)
                def test_2(self):
                    self.reslist.append(2)
                def test_3(self):
                    self.reslist.append(3)
                def test_4(self):
                    assert self.reslist == [1,2,1,2,3]
        """
        )
        passed, skipped, failed = reprec.countoutcomes()
        assert failed == skipped == 0
        assert passed == 7

    def test_collect_only_with_various_situations(self, testdir):
        """
        Tests the `--collect-only` option of pytest with various scenarios.
        
        This function runs pytest with the `--collect-only` option on a test file that contains multiple test functions and classes. It then checks the number of collected items, ensures no test runs, and verifies the number of collection start and finish events.
        
        Parameters:
        - testdir (pytest.Testdir): A pytest fixture that provides a temporary test directory.
        
        Returns:
        - None: The function asserts various conditions and does not return any value.
        """

        p = testdir.makepyfile(
            test_one="""
                def test_one():
                    raise ValueError()

                class TestX(object):
                    def test_method_one(self):
                        pass

                class TestY(TestX):
                    pass
            """,
            test_three="xxxdsadsadsadsa",
            __init__="",
        )
        reprec = testdir.inline_run("--collect-only", p.dirpath())

        itemstarted = reprec.getcalls("pytest_itemcollected")
        assert len(itemstarted) == 3
        assert not reprec.getreports("pytest_runtest_logreport")
        started = reprec.getcalls("pytest_collectstart")
        finished = reprec.getreports("pytest_collectreport")
        assert len(started) == len(finished)
        assert len(started) == 8
        colfail = [x for x in finished if x.failed]
        assert len(colfail) == 1

    def test_minus_x_import_error(self, testdir):
        testdir.makepyfile(__init__="")
        testdir.makepyfile(test_one="xxxx", test_two="yyyy")
        reprec = testdir.inline_run("-x", testdir.tmpdir)
        finished = reprec.getreports("pytest_collectreport")
        colfail = [x for x in finished if x.failed]
        assert len(colfail) == 1

    def test_minus_x_overridden_by_maxfail(self, testdir):
        testdir.makepyfile(__init__="")
        testdir.makepyfile(test_one="xxxx", test_two="yyyy", test_third="zzz")
        reprec = testdir.inline_run("-x", "--maxfail=2", testdir.tmpdir)
        finished = reprec.getreports("pytest_collectreport")
        colfail = [x for x in finished if x.failed]
        assert len(colfail) == 2


def test_plugin_specify(testdir):
    with pytest.raises(ImportError):
        testdir.parseconfig("-p", "nqweotexistent")
    # pytest.raises(ImportError,
    #    "config.do_configure(config)"
    # )


def test_plugin_already_exists(testdir):
    """
    Tests if a plugin is already configured and raises an error if it is.
    
    This function checks if the 'terminal' plugin is already configured in the test environment. If the plugin is found, it raises an error. The function takes no parameters and does not return any value. It operates on a `pytest` test environment and uses the `testdir` fixture to parse the configuration and ensure proper setup and teardown of the test environment.
    
    Key Parameters:
    - None
    
    Input:
    - A `pytest`
    """

    config = testdir.parseconfig("-p", "terminal")
    assert config.option.plugins == ["terminal"]
    config._do_configure()
    config._ensure_unconfigure()


def test_exclude(testdir):
    hellodir = testdir.mkdir("hello")
    hellodir.join("test_hello.py").write("x y syntaxerror")
    hello2dir = testdir.mkdir("hello2")
    hello2dir.join("test_hello2.py").write("x y syntaxerror")
    testdir.makepyfile(test_ok="def test_pass(): pass")
    result = testdir.runpytest("--ignore=hello", "--ignore=hello2")
    assert result.ret == 0
    result.stdout.fnmatch_lines(["*1 passed*"])


def test_exclude_glob(testdir):
    hellodir = testdir.mkdir("hello")
    hellodir.join("test_hello.py").write("x y syntaxerror")
    hello2dir = testdir.mkdir("hello2")
    hello2dir.join("test_hello2.py").write("x y syntaxerror")
    hello3dir = testdir.mkdir("hallo3")
    hello3dir.join("test_hello3.py").write("x y syntaxerror")
    subdir = testdir.mkdir("sub")
    subdir.join("test_hello4.py").write("x y syntaxerror")
    testdir.makepyfile(test_ok="def test_pass(): pass")
    result = testdir.runpytest("--ignore-glob=*h[ea]llo*")
    assert result.ret == 0
    result.stdout.fnmatch_lines(["*1 passed*"])


def test_deselect(testdir):
    """
    Deselect specific tests during pytest run.
    
    This function runs a pytest with specific tests deselected. It takes a test directory as input and modifies the tests within that directory to exclude certain tests from the run. The deselected tests are specified using the `--deselect` option with the full test path.
    
    Parameters:
    testdir (pytest.Testdir): A pytest Testdir instance representing the test directory.
    
    Example:
    >>> test_deselect(testdir)
    This will run pytest on the specified test
    """

    testdir.makepyfile(
        test_a="""
        import pytest

        def test_a1(): pass

        @pytest.mark.parametrize('b', range(3))
        def test_a2(b): pass

        class TestClass:
            def test_c1(self): pass

            def test_c2(self): pass
    """
    )
    result = testdir.runpytest(
        "-v",
        "--deselect=test_a.py::test_a2[1]",
        "--deselect=test_a.py::test_a2[2]",
        "--deselect=test_a.py::TestClass::test_c1",
    )
    assert result.ret == 0
    result.stdout.fnmatch_lines(["*3 passed, 3 deselected*"])
    for line in result.stdout.lines:
        assert not line.startswith(("test_a.py::test_a2[1]", "test_a.py::test_a2[2]"))


def test_sessionfinish_with_start(testdir):
    testdir.makeconftest(
        """
        import os
        values = []
        def pytest_sessionstart():
            values.append(os.getcwd())
            os.chdir("..")

        def pytest_sessionfinish():
            assert values[0] == os.getcwd()

    """
    )
    res = testdir.runpytest("--collect-only")
    assert res.ret == EXIT_NOTESTSCOLLECTED


@pytest.mark.parametrize("path", ["root", "{relative}/root", "{environment}/root"])
def test_rootdir_option_arg(testdir, monkeypatch, path):
    """
    Tests the functionality of the `--rootdir` option in pytest.
    
    This function sets the environment variable `PY_ROOTDIR_PATH` to the temporary directory path and uses the `--rootdir` option to specify a custom root directory for pytest. It then runs pytest on a test file located in the specified root directory and checks if the test passes.
    
    Parameters:
    testdir (pytest.Testdir): The pytest test directory fixture.
    monkeypatch (pytest.MonkeyPatch): The pytest monkeypatch fixture
    """

    monkeypatch.setenv("PY_ROOTDIR_PATH", str(testdir.tmpdir))
    path = path.format(relative=str(testdir.tmpdir), environment="$PY_ROOTDIR_PATH")

    rootdir = testdir.mkdir("root")
    rootdir.mkdir("tests")
    testdir.makepyfile(
        """
        import os
        def test_one():
            assert 1
    """
    )

    result = testdir.runpytest("--rootdir={}".format(path))
    result.stdout.fnmatch_lines(
        [
            "*rootdir: {}/root".format(testdir.tmpdir),
            "root/test_rootdir_option_arg.py *",
            "*1 passed*",
        ]
    )


def test_rootdir_wrong_option_arg(testdir):
    testdir.makepyfile(
        """
        import os
        def test_one():
            assert 1
    """
    )

    result = testdir.runpytest("--rootdir=wrong_dir")
    result.stderr.fnmatch_lines(
        ["*Directory *wrong_dir* not found. Check your '--rootdir' option.*"]
    )
atch_lines(
        ["*Directory *wrong_dir* not found. Check your '--rootdir' option.*"]
    )
your '--rootdir' option.*"]
    )
