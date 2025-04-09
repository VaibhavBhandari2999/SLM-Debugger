"""
This Python file contains a collection of tests and decorators related to Django's view decorators. It includes:

- **Decorators**: 
  - `fully_decorated`: A function that is fully decorated with various Django decorators.
  - `compose`: A utility function to compose multiple decorators.
  - `simple_dec`, `simple_dec_m`: Simple decorators for testing.
  - `myattr_dec`, `myattr2_dec`, `myattr_dec_m`, `myattr2_dec_m`: Decorators that add attributes to functions or methods.
  - `ClsDec`: A class decorator that wraps a function and adds an attribute.
  - `xframe_options_deny`, `xframe_options_sameorigin`, `xframe_options_exempt`: Decor
"""
from functools import update_wrapper, wraps
from unittest import TestCase

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import (
    login_required, permission_required, user_passes_test,
)
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.middleware.clickjacking import XFrameOptionsMiddleware
from django.test import SimpleTestCase
from django.utils.decorators import method_decorator
from django.utils.functional import keep_lazy, keep_lazy_text, lazy
from django.utils.safestring import mark_safe
from django.views.decorators.cache import (
    cache_control, cache_page, never_cache,
)
from django.views.decorators.clickjacking import (
    xframe_options_deny, xframe_options_exempt, xframe_options_sameorigin,
)
from django.views.decorators.http import (
    condition, require_GET, require_http_methods, require_POST, require_safe,
)
from django.views.decorators.vary import vary_on_cookie, vary_on_headers


def fully_decorated(request):
    """Expected __doc__"""
    return HttpResponse('<html><body>dummy</body></html>')


fully_decorated.anything = "Expected __dict__"


def compose(*functions):
    """
    Compose multiple functions into a single function.
    
    This function takes a variable number of functions as arguments and returns
    a new function that applies these functions sequentially to its input. The
    order of the functions is reversed, meaning the last function provided will
    be applied first.
    
    Args:
    *functions: A variable number of functions to be composed.
    
    Returns:
    A new function that, when called with the same arguments as the
    composed functions, will apply them in reverse
    """

    # compose(f, g)(*args, **kwargs) == f(g(*args, **kwargs))
    functions = list(reversed(functions))

    def _inner(*args, **kwargs):
        """
        _inner(*args, **kwargs) -> Any
        
        This function takes in variable arguments (*args) and keyword arguments (**kwargs). It processes these inputs through a series of functions stored in the 'functions' list.
        
        Parameters:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
        Returns:
        The final processed result after applying each function in the 'functions' list sequentially to the initial result.
        
        Important Functions:
        - functions[0]: The first
        """

        result = functions[0](*args, **kwargs)
        for f in functions[1:]:
            result = f(result)
        return result
    return _inner


full_decorator = compose(
    # django.views.decorators.http
    require_http_methods(["GET"]),
    require_GET,
    require_POST,
    require_safe,
    condition(lambda r: None, lambda r: None),

    # django.views.decorators.vary
    vary_on_headers('Accept-language'),
    vary_on_cookie,

    # django.views.decorators.cache
    cache_page(60 * 15),
    cache_control(private=True),
    never_cache,

    # django.contrib.auth.decorators
    # Apply user_passes_test twice to check #9474
    user_passes_test(lambda u: True),
    login_required,
    permission_required('change_world'),

    # django.contrib.admin.views.decorators
    staff_member_required,

    # django.utils.functional
    keep_lazy(HttpResponse),
    keep_lazy_text,
    lazy,

    # django.utils.safestring
    mark_safe,
)

fully_decorated = full_decorator(fully_decorated)


class DecoratorsTest(TestCase):

    def test_attributes(self):
        """
        Built-in decorators set certain attributes of the wrapped function.
        """
        self.assertEqual(fully_decorated.__name__, 'fully_decorated')
        self.assertEqual(fully_decorated.__doc__, 'Expected __doc__')
        self.assertEqual(fully_decorated.__dict__['anything'], 'Expected __dict__')

    def test_user_passes_test_composition(self):
        """
        The user_passes_test decorator can be applied multiple times (#9474).
        """
        def test1(user):
            user.decorators_applied.append('test1')
            return True

        def test2(user):
            user.decorators_applied.append('test2')
            return True

        def callback(request):
            return request.user.decorators_applied

        callback = user_passes_test(test1)(callback)
        callback = user_passes_test(test2)(callback)

        class DummyUser:
            pass

        class DummyRequest:
            pass

        request = DummyRequest()
        request.user = DummyUser()
        request.user.decorators_applied = []
        response = callback(request)

        self.assertEqual(response, ['test2', 'test1'])

    def test_cache_page(self):
        """
        Tests the caching behavior of views using the `cache_page` decorator.
        
        This test checks that the `cache_page` decorator correctly caches the
        output of the view function `my_view`. The decorator is applied with two
        different configurations: without specifying a custom key prefix and with
        a custom key prefix set to 'test'. In both cases, the cached view should
        return the same response when called with an `HttpRequest`.
        
        - `cache_page`: Decorator used to
        """

        def my_view(request):
            return "response"
        my_view_cached = cache_page(123)(my_view)
        self.assertEqual(my_view_cached(HttpRequest()), "response")
        my_view_cached2 = cache_page(123, key_prefix="test")(my_view)
        self.assertEqual(my_view_cached2(HttpRequest()), "response")

    def test_require_safe_accepts_only_safe_methods(self):
        """
        Test for the require_safe decorator.
        A view returns either a response or an exception.
        Refs #15637.
        """
        def my_view(request):
            return HttpResponse("OK")
        my_safe_view = require_safe(my_view)
        request = HttpRequest()
        request.method = 'GET'
        self.assertIsInstance(my_safe_view(request), HttpResponse)
        request.method = 'HEAD'
        self.assertIsInstance(my_safe_view(request), HttpResponse)
        request.method = 'POST'
        self.assertIsInstance(my_safe_view(request), HttpResponseNotAllowed)
        request.method = 'PUT'
        self.assertIsInstance(my_safe_view(request), HttpResponseNotAllowed)
        request.method = 'DELETE'
        self.assertIsInstance(my_safe_view(request), HttpResponseNotAllowed)


# For testing method_decorator, a decorator that assumes a single argument.
# We will get type arguments if there is a mismatch in the number of arguments.
def simple_dec(func):
    """
    simple_dec is a decorator that takes a function `func` as an argument and returns a new function `wrapper`. The `wrapper` function takes an argument `arg` and calls the original function `func` with the modified argument "test:" + arg. The decorator does not modify the input or output of the original function, but rather adds a prefix to the input argument before passing it to the original function.
    
    Args:
    func (function): The function to be decorated.
    
    Returns:
    """

    def wrapper(arg):
        return func("test:" + arg)
    return wraps(func)(wrapper)


simple_dec_m = method_decorator(simple_dec)


# For testing method_decorator, two decorators that add an attribute to the function
def myattr_dec(func):
    """
    myattr_dec is a decorator that wraps a function and adds a myattr attribute to the wrapped function. The wrapper function simply calls the original function with the given arguments and keyword arguments. The myattr attribute of the wrapper function is set to True.
    
    Args:
    func (function): The function to be wrapped.
    
    Returns:
    function: The wrapped function with an added myattr attribute.
    """

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.myattr = True
    return wrapper


myattr_dec_m = method_decorator(myattr_dec)


def myattr2_dec(func):
    """
    myattr2_dec is a decorator that wraps a function and adds a myattr2 attribute to the wrapped function. The wrapper function simply calls the original function with the given arguments and keyword arguments. The myattr2 attribute is set to True.
    
    Args:
    func (function): The function to be wrapped.
    
    Returns:
    function: The wrapped function with the myattr2 attribute added.
    """

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.myattr2 = True
    return wrapper


myattr2_dec_m = method_decorator(myattr2_dec)


class ClsDec:
    def __init__(self, myattr):
        self.myattr = myattr

    def __call__(self, f):
        """
        Calls the function `f` and returns the result of `f()` and the attribute `myattr`. The function `wrapped` is created by wrapping `f` with `update_wrapper`.
        
        Args:
        f (function): The function to be called.
        
        Returns:
        bool: The result of `f()` and the value of `myattr`.
        """


        def wrapped():
            return f() and self.myattr
        return update_wrapper(wrapped, f)


class MethodDecoratorTests(SimpleTestCase):
    """
    Tests for method_decorator
    """
    def test_preserve_signature(self):
        """
        Test the preservation of function signature using the `@simple_dec_m` decorator.
        
        This test checks if the `say` method of the `Test` class retains its original signature after being decorated with `@simple_dec_m`. The `say` method takes an argument `arg` and returns it unchanged. The test asserts that calling `Test().say("hello")` returns "test:hello".
        """

        class Test:
            @simple_dec_m
            def say(self, arg):
                return arg

        self.assertEqual("test:hello", Test().say("hello"))

    def test_preserve_attributes(self):
        """
        Tests the functionality of the `method_decorator` and `function_decorator` decorators.
        
        This test suite checks the behavior of the `method_decorator` and `function_decorator` decorators when applied to both methods and functions. It ensures that the decorators correctly preserve attributes and do not interfere with the original method or function's documentation and name.
        
        Important Functions:
        - `myattr_dec`: A function decorator that adds a specific attribute to the decorated function.
        - `myattr2_dec`: Another function
        """

        # Sanity check myattr_dec and myattr2_dec
        @myattr_dec
        def func():
            pass
        self.assertIs(getattr(func, 'myattr', False), True)

        @myattr2_dec
        def func():
            pass
        self.assertIs(getattr(func, 'myattr2', False), True)

        @myattr_dec
        @myattr2_dec
        def func():
            pass

        self.assertIs(getattr(func, 'myattr', False), True)
        self.assertIs(getattr(func, 'myattr2', False), False)

        # Decorate using method_decorator() on the method.
        class TestPlain:
            @myattr_dec_m
            @myattr2_dec_m
            def method(self):
                "A method"
                pass

        # Decorate using method_decorator() on both the class and the method.
        # The decorators applied to the methods are applied before the ones
        # applied to the class.
        @method_decorator(myattr_dec_m, "method")
        class TestMethodAndClass:
            @method_decorator(myattr2_dec_m)
            def method(self):
                "A method"
                pass

        # Decorate using an iterable of function decorators.
        @method_decorator((myattr_dec, myattr2_dec), 'method')
        class TestFunctionIterable:
            def method(self):
                "A method"
                pass

        # Decorate using an iterable of method decorators.
        decorators = (myattr_dec_m, myattr2_dec_m)

        @method_decorator(decorators, "method")
        class TestMethodIterable:
            def method(self):
                "A method"
                pass

        tests = (TestPlain, TestMethodAndClass, TestFunctionIterable, TestMethodIterable)
        for Test in tests:
            with self.subTest(Test=Test):
                self.assertIs(getattr(Test().method, 'myattr', False), True)
                self.assertIs(getattr(Test().method, 'myattr2', False), True)
                self.assertIs(getattr(Test.method, 'myattr', False), True)
                self.assertIs(getattr(Test.method, 'myattr2', False), True)
                self.assertEqual(Test.method.__doc__, 'A method')
                self.assertEqual(Test.method.__name__, 'method')

    def test_new_attribute(self):
        """A decorator that sets a new attribute on the method."""
        def decorate(func):
            func.x = 1
            return func

        class MyClass:
            @method_decorator(decorate)
            def method(self):
                return True

        obj = MyClass()
        self.assertEqual(obj.method.x, 1)
        self.assertIs(obj.method(), True)

    def test_bad_iterable(self):
        """
        Test that a TypeError is raised when attempting to use a set of method decorators.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: If a 'set' object is used as a decorator argument and is not subscriptable.
        
        Important Functions:
        - `method_decorator`: Decorator function used to apply multiple decorators to a method.
        - `set`: Data structure used to store the decorators.
        
        Variables:
        - `decorators`: Set containing two method decorators
        """

        decorators = {myattr_dec_m, myattr2_dec_m}
        msg = "'set' object is not subscriptable"
        with self.assertRaisesMessage(TypeError, msg):
            @method_decorator(decorators, "method")
            class TestIterable:
                def method(self):
                    "A method"
                    pass

    # Test for argumented decorator
    def test_argumented(self):
        """
        Tests the behavior of a method decorated with `ClsDec` when the decorator is initialized with `False`.
        
        Summary:
        - Class: `Test`
        - Method: `method`
        - Decorator: `ClsDec(False)`
        - Expected Output: `False`
        """

        class Test:
            @method_decorator(ClsDec(False))
            def method(self):
                return True

        self.assertIs(Test().method(), False)

    def test_descriptors(self):
        """
        Tests the behavior of a method with descriptors and decorators.
        
        This function defines a method `method` within a class `Test` that is decorated with `method_dec` and `descriptor_wrapper`. The `original_dec` decorator wraps the method, while `bound_wrapper` and `descriptor_wrapper` handle the descriptor protocol. The `method` returns the argument passed to it.
        
        Args:
        self: The instance of the class `Test`.
        
        Returns:
        int: The argument passed to the
        """


        def original_dec(wrapped):
            """
            original_dec is a decorator that takes a function `wrapped` as an argument and returns a new function `_wrapped`. The `_wrapped` function accepts an argument `arg` and calls the `wrapped` function with this argument, returning its result. This decorator can be used to modify or enhance the behavior of the `wrapped` function without changing its code directly.
            """

            def _wrapped(arg):
                return wrapped(arg)

            return _wrapped

        method_dec = method_decorator(original_dec)

        class bound_wrapper:
            def __init__(self, wrapped):
                self.wrapped = wrapped
                self.__name__ = wrapped.__name__

            def __call__(self, arg):
                return self.wrapped(arg)

            def __get__(self, instance, cls=None):
                return self

        class descriptor_wrapper:
            def __init__(self, wrapped):
                self.wrapped = wrapped
                self.__name__ = wrapped.__name__

            def __get__(self, instance, cls=None):
                return bound_wrapper(self.wrapped.__get__(instance, cls))

        class Test:
            @method_dec
            @descriptor_wrapper
            def method(self, arg):
                return arg

        self.assertEqual(Test().method(1), 1)

    def test_class_decoration(self):
        """
        @method_decorator can be used to decorate a class and its methods.
        """
        def deco(func):
            """
            deco is a decorator function that takes a function `func` as an argument and returns a new function `_wrapper`. The `_wrapper` function does not perform any specific operation and always returns True. This decorator can be used to modify the behavior of the decorated function without changing its implementation.
            """

            def _wrapper(*args, **kwargs):
                return True
            return _wrapper

        @method_decorator(deco, name="method")
        class Test:
            def method(self):
                return False

        self.assertTrue(Test().method())

    def test_tuple_of_decorators(self):
        """
        @method_decorator can accept a tuple of decorators.
        """
        def add_question_mark(func):
            """
            Decorator function `add_question_mark` that appends a question mark (`?`) to the result of the decorated function. The decorator takes any number of positional and keyword arguments and returns the result of the original function with an appended question mark.
            
            Args:
            func (function): The function to be decorated.
            
            Returns:
            function: A wrapper function that appends a question mark to the result of the original function.
            
            Usage:
            @add_question_mark
            def example_function(input_string
            """

            def _wrapper(*args, **kwargs):
                return func(*args, **kwargs) + "?"
            return _wrapper

        def add_exclamation_mark(func):
            """
            Decorator function `add_exclamation_mark` that takes a function `func` as an argument and returns a new function `_wrapper`. The `_wrapper` function calls the original function `func` with any number of positional or keyword arguments and appends an exclamation mark ("!") to its result. The decorator modifies the output of the decorated function by adding an exclamation mark to the end of the returned value.
            """

            def _wrapper(*args, **kwargs):
                return func(*args, **kwargs) + "!"
            return _wrapper

        # The order should be consistent with the usual order in which
        # decorators are applied, e.g.
        #    @add_exclamation_mark
        #    @add_question_mark
        #    def func():
        #        ...
        decorators = (add_exclamation_mark, add_question_mark)

        @method_decorator(decorators, name="method")
        class TestFirst:
            def method(self):
                return "hello world"

        class TestSecond:
            @method_decorator(decorators)
            def method(self):
                return "hello world"

        self.assertEqual(TestFirst().method(), "hello world?!")
        self.assertEqual(TestSecond().method(), "hello world?!")

    def test_invalid_non_callable_attribute_decoration(self):
        """
        @method_decorator on a non-callable attribute raises an error.
        """
        msg = (
            "Cannot decorate 'prop' as it isn't a callable attribute of "
            "<class 'Test'> (1)"
        )
        with self.assertRaisesMessage(TypeError, msg):
            @method_decorator(lambda: None, name="prop")
            class Test:
                prop = 1

                @classmethod
                def __module__(cls):
                    return "tests"

    def test_invalid_method_name_to_decorate(self):
        """
        @method_decorator on a nonexistent method raises an error.
        """
        msg = (
            "The keyword argument `name` must be the name of a method of the "
            "decorated class: <class 'Test'>. Got 'nonexistent_method' instead"
        )
        with self.assertRaisesMessage(ValueError, msg):
            @method_decorator(lambda: None, name='nonexistent_method')
            class Test:
                @classmethod
                def __module__(cls):
                    return "tests"


class XFrameOptionsDecoratorsTests(TestCase):
    """
    Tests for the X-Frame-Options decorators.
    """
    def test_deny_decorator(self):
        """
        Ensures @xframe_options_deny properly sets the X-Frame-Options header.
        """
        @xframe_options_deny
        def a_view(request):
            return HttpResponse()
        r = a_view(HttpRequest())
        self.assertEqual(r.headers['X-Frame-Options'], 'DENY')

    def test_sameorigin_decorator(self):
        """
        Ensures @xframe_options_sameorigin properly sets the X-Frame-Options
        header.
        """
        @xframe_options_sameorigin
        def a_view(request):
            return HttpResponse()
        r = a_view(HttpRequest())
        self.assertEqual(r.headers['X-Frame-Options'], 'SAMEORIGIN')

    def test_exempt_decorator(self):
        """
        Ensures @xframe_options_exempt properly instructs the
        XFrameOptionsMiddleware to NOT set the header.
        """
        @xframe_options_exempt
        def a_view(request):
            return HttpResponse()
        req = HttpRequest()
        resp = a_view(req)
        self.assertIsNone(resp.get('X-Frame-Options', None))
        self.assertTrue(resp.xframe_options_exempt)

        # Since the real purpose of the exempt decorator is to suppress
        # the middleware's functionality, let's make sure it actually works...
        r = XFrameOptionsMiddleware(a_view)(req)
        self.assertIsNone(r.get('X-Frame-Options', None))


class NeverCacheDecoratorTest(SimpleTestCase):
    def test_never_cache_decorator(self):
        """
        Tests the `never_cache` decorator. The `never_cache` decorator is applied to the `a_view` function, which sets the following headers in the response: Cache-Control: max-age=0, no-cache, no-store, must-revalidate, private. The test verifies that these headers are correctly set by comparing the expected values with the actual headers returned by the view function when called with an HttpRequest object.
        """

        @never_cache
        def a_view(request):
            return HttpResponse()
        r = a_view(HttpRequest())
        self.assertEqual(
            set(r.headers['Cache-Control'].split(', ')),
            {'max-age=0', 'no-cache', 'no-store', 'must-revalidate', 'private'},
        )

    def test_never_cache_decorator_http_request(self):
        """
        Tests the never_cache decorator with an HTTP request.
        
        This function checks if the `never_cache` decorator correctly receives an HttpRequest object when applied to a view method within a class. It uses a custom class `MyClass` with a method `a_view` decorated by `never_cache`. The function raises a TypeError if the decorator does not receive an HttpRequest, indicating that the decorator is not properly handling the request object. The `@method_decorator` should be used if the decorator is applied to a
        """

        class MyClass:
            @never_cache
            def a_view(self, request):
                return HttpResponse()
        msg = (
            "never_cache didn't receive an HttpRequest. If you are decorating "
            "a classmethod, be sure to use @method_decorator."
        )
        with self.assertRaisesMessage(TypeError, msg):
            MyClass().a_view(HttpRequest())


class CacheControlDecoratorTest(SimpleTestCase):
    def test_cache_control_decorator_http_request(self):
        """
        Tests the cache_control decorator with an HTTP request.
        
        This function checks if the `cache_control` decorator correctly receives an HttpRequest object when applied to a class method. It uses a custom class `MyClass` with a method `a_view` decorated by `cache_control`. The test asserts that calling `a_view` with an HttpRequest instance raises a TypeError, indicating that the decorator is not properly handling the request object. Important functions: `cache_control`, `HttpResponse`, `method_decorator`, `assert
        """

        class MyClass:
            @cache_control(a='b')
            def a_view(self, request):
                return HttpResponse()

        msg = (
            "cache_control didn't receive an HttpRequest. If you are "
            "decorating a classmethod, be sure to use @method_decorator."
        )
        with self.assertRaisesMessage(TypeError, msg):
            MyClass().a_view(HttpRequest())
