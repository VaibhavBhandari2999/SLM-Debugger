import pytest
from _pytest import python
from _pytest import runner


class TestOEJSKITSpecials:
    def test_funcarg_non_pycollectobj(self, testdir):  # rough jstests usage
        """
        Tests the behavior of the `pytest_pycollect_makeitem` hook in pytest. This hook is responsible for creating custom collection items for classes that match a specific name. In this test, a custom collector `MyCollector` is created for the class `MyClass`. The function verifies that the `arg1` fixture is correctly associated with the `MyClass` instance.
        
        Parameters:
        - testdir (pytest.Testdir): A fixture provided by pytest for creating and managing test directories.
        
        Returns:
        - None
        """

        testdir.makeconftest(
            """
            import pytest
            def pytest_pycollect_makeitem(collector, name, obj):
                if name == "MyClass":
                    return MyCollector(name, parent=collector)
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

    def test_autouse_fixture(self, testdir):  # rough jstests usage
        """
        This function tests an autouse fixture in a pytest environment.
        
        Parameters:
        testdir (pytest.Testdir): A pytest Testdir object used to create and manage test files and directories.
        
        Returns:
        None: The function does not return anything but rather modifies and collects information about the test module.
        
        Description:
        The function creates a custom pytest collector and fixture for a test module. It then collects the test class and fills its function arguments. The autouse fixture is expected to be applied to all test
        """

        testdir.makeconftest(
            """
            import pytest
            def pytest_pycollect_makeitem(collector, name, obj):
                if name == "MyClass":
                    return MyCollector(name, parent=collector)
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
    This function tests the unwrapping of a wrapped function using `getfslineno`.
    
    The function `test_wrapped_getfslineno` defines a `func` and a `wrap` function. The `wrap` function is used to wrap `func` and add attributes to it. The `wrapped_func` is then wrapped using `wrap`. The `getfslineno` function is used to get the file and line number of the wrapped function and the wrapper function.
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

    @pytest.mark.xfail(
        strict=False, reason="getfuncargnames breaks if mock is imported"
    )
    def test_wrapped_getfuncargnames_patching(self):
        from _pytest.compat import getfuncargnames

        def wrap(f):
            def func():
                pass

            func.__wrapped__ = f
            func.patchings = ["qwe"]
            return func

        @wrap
        def f(x, y, z):
            pass

        values = getfuncargnames(f)
        assert values == ("y", "z")

    def test_unittest_mock(self, testdir):
        pytest.importorskip("unittest.mock")
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
        pytest.importorskip("unittest.mock")
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
        pytest.importorskip("unittest.mock")
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

    def test_mock(self, testdir):
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
        rep
kepyfile(
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
    """
    Test that the pytestconfig fixture is session-scoped.
    
    This function checks the scope of the pytestconfig fixture, which is used to access configuration options set in pytest. The pytestconfig fixture is session-scoped, meaning it is shared across all tests within a single test session.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    The pytestconfig fixture is used to access configuration options set in pytest. This function verifies that the pytestconfig fixture has a scope of 'session', indicating that it
    """

    from _pytest.fixtures import pytestconfig

    assert pytestconfig._pytestfixturefunction.scope == "session"


class TestNoselikeTestAttribute:
    def test_module_with_global_test(self, testdir):
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
