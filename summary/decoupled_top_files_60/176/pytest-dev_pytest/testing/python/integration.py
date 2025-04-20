import pytest
from _pytest import python
from _pytest import runner


class TestOEJSKITSpecials:
    def test_funcarg_non_pycollectobj(self, testdir, recwarn):  # rough jstests usage
        """
        Tests the behavior of `pytest_pycollect_makeitem` hook in a custom collector class.
        
        This function verifies that the `pytest_pycollect_makeitem` hook correctly identifies and returns a custom collector for a specific class. It also ensures that the custom collector is used to instantiate the class and that the `funcargs` are properly filled.
        
        Parameters:
        testdir (pytest.Testdir): A pytest fixture that provides a temporary test directory.
        recwarn (pytest.WarningsCollector): A pytest fixture that
        """

        testdir.makeconftest(
            """
            import pytest
            def pytest_pycollect_makeitem(collector, name, obj):
                if name == "MyClass":
                    return MyCollector.from_parent(collector, name=name)
            class MyCollector(pytest.Collector):
                def reportinfo(self):
                    return self.fspath, 3, "xyz"
        """
        )
        modcol = testdir.getmodulecol(
            """
            import pytest
            @pytest.fixture
            def arg1(request):
                return 42
            class MyClass(object):
                pass
        """
        )
        # this hook finds funcarg factories
        rep = runner.collect_one_node(collector=modcol)
        clscol = rep.result[0]
        clscol.obj = lambda arg1: None
        clscol.funcargs = {}
        pytest._fillfuncargs(clscol)
        assert clscol.funcargs["arg1"] == 42

    def test_autouse_fixture(self, testdir, recwarn):  # rough jstests usage
        testdir.makeconftest(
            """
            import pytest
            def pytest_pycollect_makeitem(collector, name, obj):
                if name == "MyClass":
                    return MyCollector.from_parent(collector, name=name)
            class MyCollector(pytest.Collector):
                def reportinfo(self):
                    return self.fspath, 3, "xyz"
        """
        )
        modcol = testdir.getmodulecol(
            """
            import pytest
            @pytest.fixture(autouse=True)
            def hello():
                pass
            @pytest.fixture
            def arg1(request):
                return 42
            class MyClass(object):
                pass
        """
        )
        # this hook finds funcarg factories
        rep = runner.collect_one_node(modcol)
        clscol = rep.result[0]
        clscol.obj = lambda: None
        clscol.funcargs = {}
        pytest._fillfuncargs(clscol)
        assert not clscol.funcargs


def test_wrapped_getfslineno():
    """
    This function tests the unwrapping of a wrapped function using getfslineno.
    
    The function `test_wrapped_getfslineno` wraps a function `func` with another function `wrap`. The `wrap` function sets the `__wrapped__` attribute of `func` to itself and adds a `patchings` attribute. It then returns the wrapped function `wrapped_func`.
    
    The `getfslineno` function is used to get the file and line number of the
    """

    def func():
        pass

    def wrap(f):
        func.__wrapped__ = f
        func.patchings = ["qwe"]
        return func

    @wrap
    def wrapped_func(x, y, z):
        pass

    fs, lineno = python.getfslineno(wrapped_func)
    fs2, lineno2 = python.getfslineno(wrap)
    assert lineno > lineno2, "getfslineno does not unwrap correctly"


class TestMockDecoration:
    def test_wrapped_getfuncargnames(self):
        """
        Test the wrapped function to retrieve the function argument names.
        
        This function tests the `getfuncargnames` function from `_pytest.compat` by wrapping a function `f` with another function `wrap`. The `wrap` function assigns the original function `f` to `__wrapped__` attribute of the wrapper function. The `getfuncargnames` function is then used to retrieve the argument names of the wrapped function `f`. The test asserts that the returned argument names are `('x',
        """

        from _pytest.compat import getfuncargnames

        def wrap(f):
            def func():
                pass

            func.__wrapped__ = f
            return func

        @wrap
        def f(x):
            pass

        values = getfuncargnames(f)
        assert values == ("x",)

    def test_getfuncargnames_patching(self):
        from _pytest.compat import getfuncargnames
        from unittest.mock import patch

        class T:
            def original(self, x, y, z):
                pass

        @patch.object(T, "original")
        def f(x, y, z):
            pass

        values = getfuncargnames(f)
        assert values == ("y", "z")

    def test_unittest_mock(self, testdir):
        testdir.makepyfile(
            """
            import unittest.mock
            class T(unittest.TestCase):
                @unittest.mock.patch("os.path.abspath")
                def test_hello(self, abspath):
                    import os
                    os.path.abspath("hello")
                    abspath.assert_any_call("hello")
        """
        )
        reprec = testdir.inline_run()
        reprec.assertoutcome(passed=1)

    def test_unittest_mock_and_fixture(self, testdir):
        """
        This function tests the interaction between unittest.mock and fixtures in a pytest environment.
        
        Parameters:
        testdir (pytest.Testdir): A pytest Testdir object used to create and run test files.
        
        The function creates a test file with a fixture and a test function that uses unittest.mock to mock the `os.path.abspath` method. The test fixture `inject_me` is not used in the test function. The test function `test_hello` calls `os.path.abspath` with the argument "hello" and
        """

        testdir.makepyfile(
            """
            import os.path
            import unittest.mock
            import pytest

            @pytest.fixture
            def inject_me():
                pass

            @unittest.mock.patch.object(os.path, "abspath",
                                        new=unittest.mock.MagicMock)
            def test_hello(inject_me):
                import os
                os.path.abspath("hello")
        """
        )
        reprec = testdir.inline_run()
        reprec.assertoutcome(passed=1)

    def test_unittest_mock_and_pypi_mock(self, testdir):
        pytest.importorskip("mock", "1.0.1")
        testdir.makepyfile(
            """
            import mock
            import unittest.mock
            class TestBoth(object):
                @unittest.mock.patch("os.path.abspath")
                def test_hello(self, abspath):
                    import os
                    os.path.abspath("hello")
                    abspath.assert_any_call("hello")

                @mock.patch("os.path.abspath")
                def test_hello_mock(self, abspath):
                    import os
                    os.path.abspath("hello")
                    abspath.assert_any_call("hello")
        """
        )
        reprec = testdir.inline_run()
        reprec.assertoutcome(passed=2)

    def test_mock_sentinel_check_against_numpy_like(self, testdir):
        """Ensure our function that detects mock arguments compares against sentinels using
        identity to circumvent objects which can't be compared with equality against others
        in a truth context, like with numpy arrays (#5606).
        """
        testdir.makepyfile(
            dummy="""
            class NumpyLike:
                def __init__(self, value):
                    self.value = value
                def __eq__(self, other):
                    raise ValueError("like numpy, cannot compare against others for truth")
            FOO = NumpyLike(10)
        """
        )
        testdir.makepyfile(
            """
            from unittest.mock import patch
            import dummy
            class Test(object):
                @patch("dummy.FOO", new=dummy.NumpyLike(50))
                def test_hello(self):
                    assert dummy.FOO.value == 50
        """
        )
        reprec = testdir.inline_run()
        reprec.assertoutcome(passed=1)

    def test_mock(self, testdir):
        """
        This function tests the usage of the `mock` library in Python. It checks the functionality of `mock.patch` in two different test cases.
        
        Parameters:
        - testdir: The test directory object used to create and run test files.
        
        Returns:
        - None: The function runs the tests and asserts the outcomes.
        
        Key Points:
        - The function imports the `mock` library and uses it to patch the `os.path.abspath` and `os.path.normpath` functions.
        - Two test cases are defined
        """

        pytest.importorskip("mock", "1.0.1")
        testdir.makepyfile(
            """
            import os
            import unittest
            import mock

            class T(unittest.TestCase):
                @mock.patch("os.path.abspath")
                def test_hello(self, abspath):
                    os.path.abspath("hello")
                    abspath.assert_any_call("hello")
            def mock_basename(path):
                return "mock_basename"
            @mock.patch("os.path.abspath")
            @mock.patch("os.path.normpath")
            @mock.patch("os.path.basename", new=mock_basename)
            def test_someting(normpath, abspath, tmpdir):
                abspath.return_value = "this"
                os.path.normpath(os.path.abspath("hello"))
                normpath.assert_any_call("this")
                assert os.path.basename("123") == "mock_basename"
        """
        )
        reprec = testdir.inline_run()
        reprec.assertoutcome(passed=2)
        calls = reprec.getcalls("pytest_runtest_logreport")
        funcnames = [
            call.report.location[2] for call in calls if call.report.when == "call"
        ]
        assert funcnames == ["T.test_hello", "test_someting"]

    def test_mock_sorting(self, testdir):
        pytest.importorskip("mock", "1.0.1")
        testdir.makepyfile(
            """
            import os
            import mock

            @mock.patch("os.path.abspath")
            def test_one(abspath):
                pass
            @mock.patch("os.path.abspath")
            def test_two(abspath):
                pass
            @mock.patch("os.path.abspath")
            def test_three(abspath):
                pass
        """
        )
        reprec = testdir.inline_run()
        calls = reprec.getreports("pytest_runtest_logreport")
        calls = [x for x in calls if x.when == "call"]
        names = [x.nodeid.split("::")[-1] for x in calls]
        assert names == ["test_one", "test_two", "test_three"]

    def test_mock_double_patch_issue473(self, testdir):
        pytest.importorskip("mock", "1.0.1")
        testdir.makepyfile(
            """
            from mock import patch
            from pytest import mark

            @patch('os.getcwd')
            @patch('os.path')
            @mark.slow
            class TestSimple(object):
                def test_simple_thing(self, mock_path, mock_getcwd):
                    pass
        """
        )
        reprec = testdir.inline_run()
        reprec.assertoutcome(passed=1)


class TestReRunTests:
    def test_rerun(self, testdir):
        testdir.makeconftest(
            """
            from _pytest.runner import runtestprotocol
            def pytest_runtest_protocol(item, nextitem):
                runtestprotocol(item, log=False, nextitem=nextitem)
                runtestprotocol(item, log=True, nextitem=nextitem)
        """
        )
        testdir.makepyfile(
            """
            import pytest
            count = 0
            req = None
            @pytest.fixture
            def fix(request):
                global count, req
                assert request != req
                req = request
                print("fix count %s" % count)
                count += 1
            def test_fix(fix):
                pass
        """
        )
        result = testdir.runpytest("-s")
        result.stdout.fnmatch_lines(
            """
            *fix count 0*
            *fix count 1*
        """
        )
        result.stdout.fnmatch_lines(
            """
            *2 passed*
        """
        )


def test_pytestconfig_is_session_scoped():
    from _pytest.fixtures import pytestconfig

    assert pytestconfig._pytestfixturefunction.scope == "session"


class TestNoselikeTestAttribute:
    def test_module_with_global_test(self, testdir):
        """
        Tests a module with a global test flag.
        
        This function runs a test on a specified module that contains a global test flag. The module is defined in the test file and is checked for the presence of the `__test__` flag. If the flag is set to `False`, the test is skipped. The function returns a report indicating whether the test was successfully run or not.
        
        Parameters:
        testdir (pytest.Testdir): The test directory object containing the test file.
        
        Returns:
        list
        """

        testdir.makepyfile(
            """
            __test__ = False
            def test_hello():
                pass
        """
        )
        reprec = testdir.inline_run()
        assert not reprec.getfailedcollections()
        calls = reprec.getreports("pytest_runtest_logreport")
        assert not calls

    def test_class_and_method(self, testdir):
        testdir.makepyfile(
            """
            __test__ = True
            def test_func():
                pass
            test_func.__test__ = False

            class TestSome(object):
                __test__ = False
                def test_method(self):
                    pass
        """
        )
        reprec = testdir.inline_run()
        assert not reprec.getfailedcollections()
        calls = reprec.getreports("pytest_runtest_logreport")
        assert not calls

    def test_unittest_class(self, testdir):
        testdir.makepyfile(
            """
            import unittest
            class TC(unittest.TestCase):
                def test_1(self):
                    pass
            class TC2(unittest.TestCase):
                __test__ = False
                def test_2(self):
                    pass
        """
        )
        reprec = testdir.inline_run()
        assert not reprec.getfailedcollections()
        call = reprec.getcalls("pytest_collection_modifyitems")[0]
        assert len(call.items) == 1
        assert call.items[0].cls.__name__ == "TC"

    def test_class_with_nasty_getattr(self, testdir):
        """Make sure we handle classes with a custom nasty __getattr__ right.

        With a custom __getattr__ which e.g. returns a function (like with a
        RPC wrapper), we shouldn't assume this meant "__test__ = True".
        """
        # https://github.com/pytest-dev/pytest/issues/1204
        testdir.makepyfile(
            """
            class MetaModel(type):

                def __getattr__(cls, key):
                    return lambda: None


            BaseModel = MetaModel('Model', (), {})


            class Model(BaseModel):

                __metaclass__ = MetaModel

                def test_blah(self):
                    pass
        """
        )
        reprec = testdir.inline_run()
        assert not reprec.getfailedcollections()
        call = reprec.getcalls("pytest_collection_modifyitems")[0]
        assert not call.items


class TestParameterize:
    """#351"""

    def test_idfn_marker(self, testdir):
        testdir.makepyfile(
            """
            import pytest

            def idfn(param):
                if param == 0:
                    return 'spam'
                elif param == 1:
                    return 'ham'
                else:
                    return None

            @pytest.mark.parametrize('a,b', [(0, 2), (1, 2)], ids=idfn)
            def test_params(a, b):
                pass
        """
        )
        res = testdir.runpytest("--collect-only")
        res.stdout.fnmatch_lines(["*spam-2*", "*ham-2*"])

    def test_idfn_fixture(self, testdir):
        testdir.makepyfile(
            """
            import pytest

            def idfn(param):
                if param == 0:
                    return 'spam'
                elif param == 1:
                    return 'ham'
                else:
                    return None

            @pytest.fixture(params=[0, 1], ids=idfn)
            def a(request):
                return request.param

            @pytest.fixture(params=[1, 2], ids=idfn)
            def b(request):
                return request.param

            def test_params(a, b):
                pass
        """
        )
        res = testdir.runpytest("--collect-only")
        res.stdout.fnmatch_lines(["*spam-2*", "*ham-2*"])
