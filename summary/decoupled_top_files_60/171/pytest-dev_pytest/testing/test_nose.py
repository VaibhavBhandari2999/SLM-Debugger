# encoding: utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pytest


def setup_module(mod):
    mod.nose = pytest.importorskip("nose")


def test_nose_setup(testdir):
    p = testdir.makepyfile(
        """
        values = []
        from nose.tools import with_setup

        @with_setup(lambda: values.append(1), lambda: values.append(2))
        def test_hello():
            assert values == [1]

        def test_world():
            assert values == [1,2]

        test_hello.setup = lambda: values.append(1)
        test_hello.teardown = lambda: values.append(2)
    """
    )
    result = testdir.runpytest(p, "-p", "nose")
    result.assert_outcomes(passed=2)


def test_setup_func_with_setup_decorator():
    """
    This function tests a setup function using the pytest fixture decorator. It creates a class A with a fixture method 'f' that appends 1 to the 'values' list. The function then calls the fixture method on an instance of class A and checks if the 'values' list is empty, indicating that the fixture did not run as expected.
    
    Key Parameters:
    - None
    
    Returns:
    - None
    
    Note:
    - The function uses the pytest fixture decorator with autouse=True to automatically run the fixture
    """

    from _pytest.nose import call_optional

    values = []

    class A(object):
        @pytest.fixture(autouse=True)
        def f(self):
            values.append(1)

    call_optional(A(), "f")
    assert not values


def test_setup_func_not_callable():
    from _pytest.nose import call_optional

    class A(object):
        f = 1

    call_optional(A(), "f")


def test_nose_setup_func(testdir):
    """
    Tests a setup and teardown function using nose's with_setup decorator.
    
    This function creates a test case that uses the `with_setup` decorator from nose.tools to define custom setup and teardown functions. The setup function appends the value 1 to a list, and the teardown function appends the value 2 to the same list. The test_hello function checks that the list contains only the value 1, while the test_world function checks that the list contains both 1 and 2.
    
    Parameters:
    """

    p = testdir.makepyfile(
        """
        from nose.tools import with_setup

        values = []

        def my_setup():
            a = 1
            values.append(a)

        def my_teardown():
            b = 2
            values.append(b)

        @with_setup(my_setup, my_teardown)
        def test_hello():
            print(values)
            assert values == [1]

        def test_world():
            print(values)
            assert values == [1,2]

    """
    )
    result = testdir.runpytest(p, "-p", "nose")
    result.assert_outcomes(passed=2)


def test_nose_setup_func_failure(testdir):
    """
    This function tests a setup function failure in a Python script using the `pytest` and `nose` frameworks. It defines a test function `test_hello` that uses the `with_setup` decorator from `nose.tools` to specify a setup function `my_setup` and a teardown function `my_teardown`. The setup function is a lambda that takes an argument `x` but does not use it, while the teardown function is also a lambda that takes an argument `x` but does
    """

    p = testdir.makepyfile(
        """
        from nose.tools import with_setup

        values = []
        my_setup = lambda x: 1
        my_teardown = lambda x: 2

        @with_setup(my_setup, my_teardown)
        def test_hello():
            print(values)
            assert values == [1]

        def test_world():
            print(values)
            assert values == [1,2]

    """
    )
    result = testdir.runpytest(p, "-p", "nose")
    result.stdout.fnmatch_lines(["*TypeError: <lambda>()*"])


def test_nose_setup_func_failure_2(testdir):
    testdir.makepyfile(
        """
        values = []

        my_setup = 1
        my_teardown = 2

        def test_hello():
            assert values == []

        test_hello.setup = my_setup
        test_hello.teardown = my_teardown
    """
    )
    reprec = testdir.inline_run()
    reprec.assertoutcome(passed=1)


def test_nose_setup_partial(testdir):
    """
    Function to test the setup and teardown functionality in nose using partial functions.
    
    This function creates a test file with a setup and teardown function that are partially applied using the `functools.partial` method. The setup function appends the value 1 to a list and the teardown function appends the value 2 to the same list. The test functions `test_hello` and `test_world` are associated with these setup and teardown functions. The test file is then executed using pytest with the nose plugin
    """

    pytest.importorskip("functools")
    p = testdir.makepyfile(
        """
        from functools import partial

        values = []

        def my_setup(x):
            a = x
            values.append(a)

        def my_teardown(x):
            b = x
            values.append(b)

        my_setup_partial = partial(my_setup, 1)
        my_teardown_partial = partial(my_teardown, 2)

        def test_hello():
            print(values)
            assert values == [1]

        def test_world():
            print(values)
            assert values == [1,2]

        test_hello.setup = my_setup_partial
        test_hello.teardown = my_teardown_partial
    """
    )
    result = testdir.runpytest(p, "-p", "nose")
    result.stdout.fnmatch_lines(["*2 passed*"])


def test_module_level_setup(testdir):
    testdir.makepyfile(
        """
        from nose.tools import with_setup
        items = {}

        def setup():
            items[1]=1

        def teardown():
            del items[1]

        def setup2():
            items[2] = 2

        def teardown2():
            del items[2]

        def test_setup_module_setup():
            assert items[1] == 1

        @with_setup(setup2, teardown2)
        def test_local_setup():
            assert items[2] == 2
            assert 1 not in items
    """
    )
    result = testdir.runpytest("-p", "nose")
    result.stdout.fnmatch_lines(["*2 passed*"])


def test_nose_style_setup_teardown(testdir):
    testdir.makepyfile(
        """
        values = []

        def setup_module():
            values.append(1)

        def teardown_module():
            del values[0]

        def test_hello():
            assert values == [1]

        def test_world():
            assert values == [1]
        """
    )
    result = testdir.runpytest("-p", "nose")
    result.stdout.fnmatch_lines(["*2 passed*"])


def test_nose_setup_ordering(testdir):
    """
    Tests the setup ordering in a test module.
    
    This function creates a test module with a setup_module function and a test class. The setup_module function sets a flag 'visited' to True. The test class has a setup method that asserts the flag is True and a test method 'test_first' that does not perform any actions. The function runs pytest on the test module and checks if the test passes.
    
    Parameters:
    testdir (pytest.Testdir): A pytest fixture that provides utilities to create and run
    """

    testdir.makepyfile(
        """
        def setup_module(mod):
            mod.visited = True

        class TestClass(object):
            def setup(self):
                assert visited
            def test_first(self):
                pass
        """
    )
    result = testdir.runpytest()
    result.stdout.fnmatch_lines(["*1 passed*"])


def test_apiwrapper_problem_issue260(testdir):
    """
    Tests the behavior of a test case in unittest when using a custom setup and teardown method. This function creates a test case with a custom setup and teardown method, which should not be called in unittest test cases. The function runs pytest and checks that the test passes without errors.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest fixture that provides a temporary directory for test files.
    
    Returns:
    - None: The function asserts that the test passes without errors.
    """

    # this would end up trying a call an optional teardown on the class
    # for plain unittests we dont want nose behaviour
    testdir.makepyfile(
        """
        import unittest
        class TestCase(unittest.TestCase):
            def setup(self):
                #should not be called in unittest testcases
                assert 0, 'setup'
            def teardown(self):
                #should not be called in unittest testcases
                assert 0, 'teardown'
            def setUp(self):
                print('setup')
            def tearDown(self):
                print('teardown')
            def test_fun(self):
                pass
        """
    )
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


def test_setup_teardown_linking_issue265(testdir):
    # we accidentally didnt integrate nose setupstate with normal setupstate
    # this test ensures that won't happen again
    testdir.makepyfile(
        '''
        import pytest

        class TestGeneric(object):
            def test_nothing(self):
                """Tests the API of the implementation (for generic and specialized)."""

        @pytest.mark.skipif("True", reason=
                    "Skip tests to check if teardown is skipped as well.")
        class TestSkipTeardown(TestGeneric):

            def setup(self):
                """Sets up my specialized implementation for $COOL_PLATFORM."""
                raise Exception("should not call setup for skipped tests")

            def teardown(self):
                """Undoes the setup."""
                raise Exception("should not call teardown for skipped tests")
        '''
    )
    reprec = testdir.runpytest()
    reprec.assert_outcomes(passed=1, skipped=1)


def test_SkipTest_during_collection(testdir):
    """
    Tests the behavior of `nose.SkipTest` during test collection.
    
    This function creates a test file with a `nose.SkipTest` exception raised
    during collection. It then runs pytest on this file and checks that the
    test is correctly marked as skipped.
    
    Parameters:
    testdir (pytest.Testdir): A pytest fixture that provides utilities to
    create and run tests.
    
    Returns:
    None: The function asserts the outcome of the test run.
    """

    p = testdir.makepyfile(
        """
        import nose
        raise nose.SkipTest("during collection")
        def test_failing():
            assert False
        """
    )
    result = testdir.runpytest(p)
    result.assert_outcomes(skipped=1)


def test_SkipTest_in_test(testdir):
    testdir.makepyfile(
        """
        import nose

        def test_skipping():
            raise nose.SkipTest("in test")
        """
    )
    reprec = testdir.inline_run()
    reprec.assertoutcome(skipped=1)


def test_istest_function_decorator(testdir):
    p = testdir.makepyfile(
        """
        import nose.tools
        @nose.tools.istest
        def not_test_prefix():
            pass
        """
    )
    result = testdir.runpytest(p)
    result.assert_outcomes(passed=1)


def test_nottest_function_decorator(testdir):
    """
    Tests a function decorated with `nose.tools.nottest` to ensure it is not executed by pytest.
    
    This function creates a test file with a function decorated using `nose.tools.nottest`. The purpose is to verify that the decorated function is not run by pytest, and no test reports are generated for it.
    
    Parameters:
    - testdir (pytest.Testdir): A pytest test directory fixture used to create and run test files.
    
    Returns:
    - None: The function asserts that the decorated function
    """

    testdir.makepyfile(
        """
        import nose.tools
        @nose.tools.nottest
        def test_prefix():
            pass
        """
    )
    reprec = testdir.inline_run()
    assert not reprec.getfailedcollections()
    calls = reprec.getreports("pytest_runtest_logreport")
    assert not calls


def test_istest_class_decorator(testdir):
    p = testdir.makepyfile(
        """
        import nose.tools
        @nose.tools.istest
        class NotTestPrefix(object):
            def test_method(self):
                pass
        """
    )
    result = testdir.runpytest(p)
    result.assert_outcomes(passed=1)


def test_nottest_class_decorator(testdir):
    testdir.makepyfile(
        """
        import nose.tools
        @nose.tools.nottest
        class TestPrefix(object):
            def test_method(self):
                pass
        """
    )
    reprec = testdir.inline_run()
    assert not reprec.getfailedcollections()
    calls = reprec.getreports("pytest_runtest_logreport")
    assert not calls


def test_skip_test_with_unicode(testdir):
    """
    Tests a function that creates a Python test class with a test method that raises a SkipTest exception with a Unicode string. The function compiles the test file and runs pytest to check if the test is correctly marked as skipped.
    
    Parameters:
    testdir (pytest.Testdir): A pytest fixture that provides utilities to create and run test files.
    
    Returns:
    result (pytest.Result): The result object from running pytest, which contains information about the test run, including the number of tests skipped, passed,
    """

    testdir.makepyfile(
        """
        # encoding: utf-8
        import unittest
        class TestClass():
            def test_io(self):
                raise unittest.SkipTest(u'😊')
    """
    )
    result = testdir.runpytest()
    result.stdout.fnmatch_lines(["* 1 skipped *"])
