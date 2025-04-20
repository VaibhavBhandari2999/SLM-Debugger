import pytest
from _pytest import python
from _pytest import runner


class TestOEJSKITSpecials:
    def test_funcarg_non_pycollectobj(self, testdir, recwarn):  # rough jstests usage
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
        """
        This function tests the usage of autouse fixtures in pytest. It involves creating a custom collector for a specific class and then collecting the function arguments for an instance of that class.
        
        Parameters:
        testdir (pytest.Testdir): A pytest Testdir object used to create and manage test files and directories.
        recwarn (pytest.WarningsRecorder): A pytest WarningsRecorder object used to record warnings.
        
        Returns:
        None: The function does not return anything but performs assertions on the collected function arguments.
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
    Get the filename and line number of the wrapped function.
    
    This function retrieves the filename and line number of the wrapped function
    inside the `wrap` decorator. It ensures that the original function's details
    are preserved even after being wrapped.
    
    Parameters:
    wrapped_func (function): The wrapped function for which to get the filename and line number.
    
    Returns:
    tuple: A tuple containing the filename and line number of the wrapped function.
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
        """
        This function tests the usage of the unittest.mock library to patch the os.path.abspath function. It creates a test case where the patched function is called with the argument "hello" and then asserts that the mock function was called with the same argument.
        
        Parameters:
        testdir (pytest.Testdir): A pytest Testdir object used to create and run test files.
        
        Returns:
        None: The function asserts that the test case passes and does not return any value.
        
        Key Points:
        - A test file is
        """

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
        - testdir (pytest.Testdir): A pytest test directory object used to create and run test files.
        
        Returns:
        - None: The function runs the tests and checks the outcome.
        
        Key Points:
        - The function creates a test file with two test cases.
        - The first test case (`test_hello`) uses `mock.patch` to mock the `
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
        """
        This function tests the ordering of mock patching in a set of test functions.
        
        Parameters:
        testdir (pytest.Testdir): A pytest test directory object used to create and run test files.
        
        Returns:
        None: The function asserts that the test functions are called in the expected order.
        
        Key Points:
        - The function uses `pytest.importorskip` to ensure that the `mock` library is available and of a minimum version.
        - A test file is created with three test functions, each patched
        """

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
        """
        This function tests the rerun functionality of pytest. It configures a custom pytest_runtest_protocol hook in a conftest file to rerun each test twice. The function also defines a pytest fixture that is used to assert the uniqueness of the request object across different runs. The test case verifies that the fixture is called twice for each test, indicating that the test is rerun. The function returns the result of the pytest run, which should indicate that all tests passed.
        
        Parameters:
        - testdir
        """

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
        """
        Tests the pytest collection and execution behavior for classes and methods with the `__test__` attribute.
        
        Parameters:
        testdir (pytest.Testdir): A pytest fixture that provides a temporary test directory.
        
        The function creates a test file with a function and a class, both of which have the `__test__` attribute set to `False`. It then runs the tests and checks that no collections or reports are generated, indicating that the `__test__` attribute successfully excluded these items from the test
        """

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
        """
        Tests the `idfn` function within a pytest.mark.parametrize decorator.
        
        This function runs a pytest test suite that includes a custom `idfn` function for parameterized tests. The `idfn` function is used to generate unique identifiers for test parameters. The test suite includes two parameterized test cases, each with a unique identifier based on the `idfn` function.
        
        Parameters:
        testdir (pytest.Testdir): A pytest fixture that provides a temporary test directory.
        
        Returns:
        None:
        """

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
