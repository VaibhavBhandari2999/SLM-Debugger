import asyncio
import logging
import re
import sys
import time
import warnings
from contextlib import contextmanager
from functools import wraps
from io import StringIO
from itertools import chain
from types import SimpleNamespace
from unittest import TestCase, skipIf, skipUnless
from xml.dom.minidom import Node, parseString

from django.apps import apps
from django.apps.registry import Apps
from django.conf import UserSettingsHolder, settings
from django.core import mail
from django.core.exceptions import ImproperlyConfigured
from django.core.signals import request_started
from django.db import DEFAULT_DB_ALIAS, connections, reset_queries
from django.db.models.options import Options
from django.template import Template
from django.test.signals import setting_changed, template_rendered
from django.urls import get_script_prefix, set_script_prefix
from django.utils.translation import deactivate

try:
    import jinja2
except ImportError:
    jinja2 = None


__all__ = (
    'Approximate', 'ContextList', 'isolate_lru_cache', 'get_runner',
    'modify_settings', 'override_settings',
    'requires_tz_support',
    'setup_test_environment', 'teardown_test_environment',
)

TZ_SUPPORT = hasattr(time, 'tzset')


class Approximate:
    def __init__(self, val, places=7):
        self.val = val
        self.places = places

    def __repr__(self):
        return repr(self.val)

    def __eq__(self, other):
        return self.val == other or round(abs(self.val - other), self.places) == 0


class ContextList(list):
    """
    A wrapper that provides direct key access to context items contained
    in a list of context objects.
    """
    def __getitem__(self, key):
        """
        Retrieve an item from the context.
        
        This method allows retrieval of items using either a string key or an
        index. If the key is a string, it searches through all subcontexts for a
        matching key and returns the corresponding value. If no match is found,
        a KeyError is raised. If the key is not a string, the method delegates
        to the superclass's `__getitem__` method.
        
        Args:
        key (str or int): The key or index
        """

        if isinstance(key, str):
            for subcontext in self:
                if key in subcontext:
                    return subcontext[key]
            raise KeyError(key)
        else:
            return super().__getitem__(key)

    def get(self, key, default=None):
        """
        Retrieve the value associated with `key` from the dictionary. If the key is not found, return the specified `default` value.
        
        Args:
        key (Any): The key to look up in the dictionary.
        default (Any, optional): The default value to return if the key is not found. Defaults to None.
        
        Returns:
        Any: The value associated with the key, or the default value if the key is not found.
        
        Raises:
        KeyError: If the key
        """

        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __contains__(self, key):
        """
        Determines if a given key is present in the dictionary.
        
        Args:
        key: The key to check for existence in the dictionary.
        
        Returns:
        bool: True if the key exists in the dictionary, False otherwise.
        
        Raises:
        KeyError: If the key is not found in the dictionary.
        
        Notes:
        - This method attempts to access the value associated with the given key using `self[key]`.
        - If the key is not found, a `KeyError` is
        """

        try:
            self[key]
        except KeyError:
            return False
        return True

    def keys(self):
        """
        Flattened keys of subcontexts.
        """
        return set(chain.from_iterable(d for subcontext in self for d in subcontext))


def instrumented_test_render(self, context):
    """
    An instrumented Template render method, providing a signal that can be
    intercepted by the test Client.
    """
    template_rendered.send(sender=self, template=self, context=context)
    return self.nodelist.render(context)


class _TestState:
    pass


def setup_test_environment(debug=None):
    """
    Perform global pre-test setup, such as installing the instrumented template
    renderer and setting the email backend to the locmem email backend.
    """
    if hasattr(_TestState, 'saved_data'):
        # Executing this function twice would overwrite the saved values.
        raise RuntimeError(
            "setup_test_environment() was already called and can't be called "
            "again without first calling teardown_test_environment()."
        )

    if debug is None:
        debug = settings.DEBUG

    saved_data = SimpleNamespace()
    _TestState.saved_data = saved_data

    saved_data.allowed_hosts = settings.ALLOWED_HOSTS
    # Add the default host of the test client.
    settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, 'testserver']

    saved_data.debug = settings.DEBUG
    settings.DEBUG = debug

    saved_data.email_backend = settings.EMAIL_BACKEND
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

    saved_data.template_render = Template._render
    Template._render = instrumented_test_render

    mail.outbox = []

    deactivate()


def teardown_test_environment():
    """
    Perform any global post-test teardown, such as restoring the original
    template renderer and restoring the email sending functions.
    """
    saved_data = _TestState.saved_data

    settings.ALLOWED_HOSTS = saved_data.allowed_hosts
    settings.DEBUG = saved_data.debug
    settings.EMAIL_BACKEND = saved_data.email_backend
    Template._render = saved_data.template_render

    del _TestState.saved_data
    del mail.outbox


def setup_databases(verbosity, interactive, keepdb=False, debug_sql=False, parallel=0, aliases=None, **kwargs):
    """Create the test databases."""
    test_databases, mirrored_aliases = get_unique_databases_and_mirrors(aliases)

    old_names = []

    for db_name, aliases in test_databases.values():
        first_alias = None
        for alias in aliases:
            connection = connections[alias]
            old_names.append((connection, db_name, first_alias is None))

            # Actually create the database for the first connection
            if first_alias is None:
                first_alias = alias
                connection.creation.create_test_db(
                    verbosity=verbosity,
                    autoclobber=not interactive,
                    keepdb=keepdb,
                    serialize=connection.settings_dict['TEST'].get('SERIALIZE', True),
                )
                if parallel > 1:
                    for index in range(parallel):
                        connection.creation.clone_test_db(
                            suffix=str(index + 1),
                            verbosity=verbosity,
                            keepdb=keepdb,
                        )
            # Configure all other connections as mirrors of the first one
            else:
                connections[alias].creation.set_as_test_mirror(connections[first_alias].settings_dict)

    # Configure the test mirrors.
    for alias, mirror_alias in mirrored_aliases.items():
        connections[alias].creation.set_as_test_mirror(
            connections[mirror_alias].settings_dict)

    if debug_sql:
        for alias in connections:
            connections[alias].force_debug_cursor = True

    return old_names


def dependency_ordered(test_databases, dependencies):
    """
    Reorder test_databases into an order that honors the dependencies
    described in TEST[DEPENDENCIES].
    """
    ordered_test_databases = []
    resolved_databases = set()

    # Maps db signature to dependencies of all its aliases
    dependencies_map = {}

    # Check that no database depends on its own alias
    for sig, (_, aliases) in test_databases:
        all_deps = set()
        for alias in aliases:
            all_deps.update(dependencies.get(alias, []))
        if not all_deps.isdisjoint(aliases):
            raise ImproperlyConfigured(
                "Circular dependency: databases %r depend on each other, "
                "but are aliases." % aliases
            )
        dependencies_map[sig] = all_deps

    while test_databases:
        changed = False
        deferred = []

        # Try to find a DB that has all its dependencies met
        for signature, (db_name, aliases) in test_databases:
            if dependencies_map[signature].issubset(resolved_databases):
                resolved_databases.update(aliases)
                ordered_test_databases.append((signature, (db_name, aliases)))
                changed = True
            else:
                deferred.append((signature, (db_name, aliases)))

        if not changed:
            raise ImproperlyConfigured("Circular dependency in TEST[DEPENDENCIES]")
        test_databases = deferred
    return ordered_test_databases


def get_unique_databases_and_mirrors(aliases=None):
    """
    Figure out which databases actually need to be created.

    Deduplicate entries in DATABASES that correspond the same database or are
    configured as test mirrors.

    Return two values:
    - test_databases: ordered mapping of signatures to (name, list of aliases)
                      where all aliases share the same underlying database.
    - mirrored_aliases: mapping of mirror aliases to original aliases.
    """
    if aliases is None:
        aliases = connections
    mirrored_aliases = {}
    test_databases = {}
    dependencies = {}
    default_sig = connections[DEFAULT_DB_ALIAS].creation.test_db_signature()

    for alias in connections:
        connection = connections[alias]
        test_settings = connection.settings_dict['TEST']

        if test_settings['MIRROR']:
            # If the database is marked as a test mirror, save the alias.
            mirrored_aliases[alias] = test_settings['MIRROR']
        elif alias in aliases:
            # Store a tuple with DB parameters that uniquely identify it.
            # If we have two aliases with the same values for that tuple,
            # we only need to create the test database once.
            item = test_databases.setdefault(
                connection.creation.test_db_signature(),
                (connection.settings_dict['NAME'], set())
            )
            item[1].add(alias)

            if 'DEPENDENCIES' in test_settings:
                dependencies[alias] = test_settings['DEPENDENCIES']
            else:
                if alias != DEFAULT_DB_ALIAS and connection.creation.test_db_signature() != default_sig:
                    dependencies[alias] = test_settings.get('DEPENDENCIES', [DEFAULT_DB_ALIAS])

    test_databases = dict(dependency_ordered(test_databases.items(), dependencies))
    return test_databases, mirrored_aliases


def teardown_databases(old_config, verbosity, parallel=0, keepdb=False):
    """Destroy all the non-mirror databases."""
    for connection, old_name, destroy in old_config:
        if destroy:
            if parallel > 1:
                for index in range(parallel):
                    connection.creation.destroy_test_db(
                        suffix=str(index + 1),
                        verbosity=verbosity,
                        keepdb=keepdb,
                    )
            connection.creation.destroy_test_db(old_name, verbosity, keepdb)


def get_runner(settings, test_runner_class=None):
    """
    get_runner is a function that takes in two parameters: settings and test_runner_class. It returns an instance of the specified test runner class.
    
    Parameters:
    settings (object): An object containing configuration settings.
    test_runner_class (str, optional): The fully qualified name of the test runner class to be instantiated. If not provided, the value of settings.TEST_RUNNER will be used.
    
    Returns:
    object: An instance of the specified test runner class.
    
    The function first checks if
    """

    test_runner_class = test_runner_class or settings.TEST_RUNNER
    test_path = test_runner_class.split('.')
    # Allow for relative paths
    if len(test_path) > 1:
        test_module_name = '.'.join(test_path[:-1])
    else:
        test_module_name = '.'
    test_module = __import__(test_module_name, {}, {}, test_path[-1])
    return getattr(test_module, test_path[-1])


class TestContextDecorator:
    """
    A base class that can either be used as a context manager during tests
    or as a test function or unittest.TestCase subclass decorator to perform
    temporary alterations.

    `attr_name`: attribute assigned the return value of enable() if used as
                 a class decorator.

    `kwarg_name`: keyword argument passing the return value of enable() if
                  used as a function decorator.
    """
    def __init__(self, attr_name=None, kwarg_name=None):
        self.attr_name = attr_name
        self.kwarg_name = kwarg_name

    def enable(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError

    def __enter__(self):
        return self.enable()

    def __exit__(self, exc_type, exc_value, traceback):
        self.disable()

    def decorate_class(self, cls):
        """
        Decorates a given class to enable context management for setUp and tearDown methods in unittest.TestCase subclasses.
        
        Args:
        cls (type): The class to be decorated.
        
        Returns:
        type: The decorated class with modified setUp and tearDown methods.
        
        Raises:
        TypeError: If the provided class is not a subclass of unittest.TestCase.
        """

        if issubclass(cls, TestCase):
            decorated_setUp = cls.setUp
            decorated_tearDown = cls.tearDown

            def setUp(inner_self):
                """
                Sets up the test environment by enabling the context manager and optionally storing the context in an attribute of the inner_self object. If an exception occurs during the execution of the decorated setUp method, the context is disabled and the exception is re-raised.
                
                Args:
                inner_self (object): The instance of the class containing the decorated setUp method.
                
                Attributes:
                attr_name (str): The name of the attribute to store the context in (if specified).
                
                Functions:
                enable: Enables
                """

                context = self.enable()
                if self.attr_name:
                    setattr(inner_self, self.attr_name, context)
                try:
                    decorated_setUp(inner_self)
                except Exception:
                    self.disable()
                    raise

            def tearDown(inner_self):
                decorated_tearDown(inner_self)
                self.disable()

            cls.setUp = setUp
            cls.tearDown = tearDown
            return cls
        raise TypeError('Can only decorate subclasses of unittest.TestCase')

    def decorate_callable(self, func):
        """
        This function decorates a callable function. It checks if the function is an asynchronous coroutine function using `asyncio.iscoroutinefunction`. If it is, it wraps the function in an asynchronous context manager, ensuring that the `with` statement is executed at the appropriate time. If the function is not an asynchronous coroutine, it simply wraps the function in a synchronous context manager. The function also allows for an optional keyword argument (`self.kwarg_name`) to be passed to the decorated function, which
        """

        if asyncio.iscoroutinefunction(func):
            # If the inner function is an async function, we must execute async
            # as well so that the `with` statement executes at the right time.
            @wraps(func)
            async def inner(*args, **kwargs):
                with self as context:
                    if self.kwarg_name:
                        kwargs[self.kwarg_name] = context
                    return await func(*args, **kwargs)
        else:
            @wraps(func)
            def inner(*args, **kwargs):
                """
                inner(*args, **kwargs) -> callable
                
                This function takes in variable arguments (*args) and keyword arguments (**kwargs). It uses the `with` statement to execute a context manager (self) and then checks if there is a kwarg_name attribute. If so, it assigns the context to the corresponding keyword argument. Finally, it calls the original function (func) with the provided arguments and returns its result.
                
                Args:
                *args: Variable length argument list.
                **kwargs
                """

                with self as context:
                    if self.kwarg_name:
                        kwargs[self.kwarg_name] = context
                    return func(*args, **kwargs)
        return inner

    def __call__(self, decorated):
        """
        This function is a decorator factory that can be used to decorate either a class or a callable (function or method). It checks the type of the input `decorated` and applies the appropriate decoration based on whether it's a class or a callable.
        
        Parameters:
        - decorated: The class or callable to be decorated.
        
        Returns:
        - If `decorated` is a class, returns the result of `decorate_class(decorated)`.
        - If `decorated` is a
        """

        if isinstance(decorated, type):
            return self.decorate_class(decorated)
        elif callable(decorated):
            return self.decorate_callable(decorated)
        raise TypeError('Cannot decorate object of type %s' % type(decorated))


class override_settings(TestContextDecorator):
    """
    Act as either a decorator or a context manager. If it's a decorator, take a
    function and return a wrapped function. If it's a contextmanager, use it
    with the ``with`` statement. In either event, entering/exiting are called
    before and after, respectively, the function/block is executed.
    """
    enable_exception = None

    def __init__(self, **kwargs):
        self.options = kwargs
        super().__init__()

    def enable(self):
        """
        Enables a set of custom settings by overriding certain values in the
        global `settings` object. The override values are defined in the
        `self.options` dictionary. This function first attempts to set the
        `INSTALLED_APPS` setting using the provided list. If this operation fails,
        it reverts the change. It then creates a new `UserSettingsHolder` instance
        with the updated settings and applies these changes. After that, it sends
        a `setting
        """

        # Keep this code at the beginning to leave the settings unchanged
        # in case it raises an exception because INSTALLED_APPS is invalid.
        if 'INSTALLED_APPS' in self.options:
            try:
                apps.set_installed_apps(self.options['INSTALLED_APPS'])
            except Exception:
                apps.unset_installed_apps()
                raise
        override = UserSettingsHolder(settings._wrapped)
        for key, new_value in self.options.items():
            setattr(override, key, new_value)
        self.wrapped = settings._wrapped
        settings._wrapped = override
        for key, new_value in self.options.items():
            try:
                setting_changed.send(
                    sender=settings._wrapped.__class__,
                    setting=key, value=new_value, enter=True,
                )
            except Exception as exc:
                self.enable_exception = exc
                self.disable()

    def disable(self):
        """
        Disables the current settings by unsetting installed apps, restoring the wrapped settings, and handling setting changes. It also raises an exception if one was set.
        
        Args:
        self: The instance of the class containing the method.
        
        Returns:
        None
        
        Important Functions:
        - `apps.unset_installed_apps()`: Unsets the installed apps.
        - `settings._wrapped = self.wrapped`: Restores the wrapped settings.
        - `del self.wrapped`: Deletes the wrapped
        """

        if 'INSTALLED_APPS' in self.options:
            apps.unset_installed_apps()
        settings._wrapped = self.wrapped
        del self.wrapped
        responses = []
        for key in self.options:
            new_value = getattr(settings, key, None)
            responses_for_setting = setting_changed.send_robust(
                sender=settings._wrapped.__class__,
                setting=key, value=new_value, enter=False,
            )
            responses.extend(responses_for_setting)
        if self.enable_exception is not None:
            exc = self.enable_exception
            self.enable_exception = None
            raise exc
        for _, response in responses:
            if isinstance(response, Exception):
                raise response

    def save_options(self, test_func):
        """
        Saves the options to the test function's overridden settings.
        
        Args:
        test_func (function): The test function to save the options to.
        
        Summary:
        This function saves the options to the test function's overridden settings by either assigning the options directly or merging them with any existing overridden settings. It ensures that the overridden settings are not altered by using a duplicate dictionary when merging.
        """

        if test_func._overridden_settings is None:
            test_func._overridden_settings = self.options
        else:
            # Duplicate dict to prevent subclasses from altering their parent.
            test_func._overridden_settings = {
                **test_func._overridden_settings,
                **self.options,
            }

    def decorate_class(self, cls):
        """
        Decorates a Django SimpleTestCase class to save its original settings and apply overridden settings.
        
        Args:
        cls (type): The Django SimpleTestCase class to be decorated.
        
        Raises:
        ValueError: If the provided class is not a subclass of Django's SimpleTestCase.
        
        Returns:
        type: The decorated Django SimpleTestCase class with saved and overridden settings.
        """

        from django.test import SimpleTestCase
        if not issubclass(cls, SimpleTestCase):
            raise ValueError(
                "Only subclasses of Django SimpleTestCase can be decorated "
                "with override_settings")
        self.save_options(cls)
        return cls


class modify_settings(override_settings):
    """
    Like override_settings, but makes it possible to append, prepend, or remove
    items instead of redefining the entire list.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the override_settings object.
        
        Args:
        *args: Variable length argument list. If provided, the first element is expected to be an instance of operations.
        **kwargs: Arbitrary keyword arguments. If no positional arguments are provided, these key-value pairs are expected to represent the operations.
        
        Summary:
        This method initializes an override_settings object by setting its 'operations' attribute based on the provided arguments. It supports two initialization modes: one using positional arguments and another using keyword arguments. The
        """

        if args:
            # Hack used when instantiating from SimpleTestCase.setUpClass.
            assert not kwargs
            self.operations = args[0]
        else:
            assert not args
            self.operations = list(kwargs.items())
        super(override_settings, self).__init__()

    def save_options(self, test_func):
        """
        Saves the current operations to the test function's modified settings.
        
        Args:
        test_func (function): The test function to which the operations will be saved.
        
        Summary:
        This function checks if the test function has already been modified by checking its `_modified_settings` attribute. If not, it assigns the current `operations` to this attribute. Otherwise, it appends the current `operations` to the existing `_modified_settings`. The `_modified_settings` is duplicated to prevent any potential alterations
        """

        if test_func._modified_settings is None:
            test_func._modified_settings = self.operations
        else:
            # Duplicate list to prevent subclasses from altering their parent.
            test_func._modified_settings = list(
                test_func._modified_settings) + self.operations

    def enable(self):
        """
        Enables the specified operations by modifying the options dictionary. Iterates through each operation defined in `self.operations`, updates the corresponding setting in `self.options` based on the specified action ('append', 'prepend', 'remove'), and ensures that settings are cumulatively updated when called multiple times. Utilizes `settings` to retrieve initial values and performs validation on the actions.
        
        Args:
        None
        
        Returns:
        None
        
        Attributes:
        self.options (dict): Stores the modified options
        """

        self.options = {}
        for name, operations in self.operations:
            try:
                # When called from SimpleTestCase.setUpClass, values may be
                # overridden several times; cumulate changes.
                value = self.options[name]
            except KeyError:
                value = list(getattr(settings, name, []))
            for action, items in operations.items():
                # items my be a single value or an iterable.
                if isinstance(items, str):
                    items = [items]
                if action == 'append':
                    value = value + [item for item in items if item not in value]
                elif action == 'prepend':
                    value = [item for item in items if item not in value] + value
                elif action == 'remove':
                    value = [item for item in value if item not in items]
                else:
                    raise ValueError("Unsupported action: %s" % action)
            self.options[name] = value
        super().enable()


class override_system_checks(TestContextDecorator):
    """
    Act as a decorator. Override list of registered system checks.
    Useful when you override `INSTALLED_APPS`, e.g. if you exclude `auth` app,
    you also need to exclude its system checks.
    """
    def __init__(self, new_checks, deployment_checks=None):
        """
        Initialize a custom checks object.
        
        Args:
        new_checks (list): A list of new checks to be added.
        deployment_checks (list, optional): A list of deployment-specific checks. Defaults to None.
        
        Attributes:
        registry (django.core.checks.registry.Registry): The Django checks registry.
        new_checks (list): The list of new checks to be added.
        deployment_checks (list): The list of deployment-specific checks.
        """

        from django.core.checks.registry import registry
        self.registry = registry
        self.new_checks = new_checks
        self.deployment_checks = deployment_checks
        super().__init__()

    def enable(self):
        """
        Enables custom checks by unregistering existing checks and registering new ones. Modifies the registry's registered checks and deployment checks sets.
        
        Args:
        self: The instance of the class containing the registry and new checks.
        
        Summary:
        This method unregisters all currently registered checks from the registry and replaces them with new checks. It also optionally updates the deployment checks set based on the provided deployment checks list. The old checks and deployment checks are stored before being replaced.
        
        Returns:
        None
        """

        self.old_checks = self.registry.registered_checks
        self.registry.registered_checks = set()
        for check in self.new_checks:
            self.registry.register(check, *getattr(check, 'tags', ()))
        self.old_deployment_checks = self.registry.deployment_checks
        if self.deployment_checks is not None:
            self.registry.deployment_checks = set()
            for check in self.deployment_checks:
                self.registry.register(check, *getattr(check, 'tags', ()), deploy=True)

    def disable(self):
        self.registry.registered_checks = self.old_checks
        self.registry.deployment_checks = self.old_deployment_checks


def compare_xml(want, got):
    """
    Try to do a 'xml-comparison' of want and got. Plain string comparison
    doesn't always work because, for example, attribute ordering should not be
    important. Ignore comment nodes, processing instructions, document type
    node, and leading and trailing whitespaces.

    Based on https://github.com/lxml/lxml/blob/master/src/lxml/doctestcompare.py
    """
    _norm_whitespace_re = re.compile(r'[ \t\n][ \t\n]+')

    def norm_whitespace(v):
        return _norm_whitespace_re.sub(' ', v)

    def child_text(element):
        return ''.join(c.data for c in element.childNodes
                       if c.nodeType == Node.TEXT_NODE)

    def children(element):
        return [c for c in element.childNodes
                if c.nodeType == Node.ELEMENT_NODE]

    def norm_child_text(element):
        return norm_whitespace(child_text(element))

    def attrs_dict(element):
        return dict(element.attributes.items())

    def check_element(want_element, got_element):
        """
        Check if two XML elements match.
        
        This function compares two XML elements based on their tag names, child text content, attributes, and recursively checks their child elements.
        
        Args:
        want_element (Element): The reference XML element to compare against.
        got_element (Element): The actual XML element to be compared.
        
        Returns:
        bool: True if both elements match, False otherwise.
        """

        if want_element.tagName != got_element.tagName:
            return False
        if norm_child_text(want_element) != norm_child_text(got_element):
            return False
        if attrs_dict(want_element) != attrs_dict(got_element):
            return False
        want_children = children(want_element)
        got_children = children(got_element)
        if len(want_children) != len(got_children):
            return False
        return all(check_element(want, got) for want, got in zip(want_children, got_children))

    def first_node(document):
        """
        Find the first non-comment, non-document type, and non-processing instruction node in a given XML or HTML document.
        
        Args:
        document (xml.dom.minidom.Document): The XML or HTML document to search through.
        
        Returns:
        xml.dom.minidom.Node: The first node that is not a comment, document type, or processing instruction node.
        """

        for node in document.childNodes:
            if node.nodeType not in (
                Node.COMMENT_NODE,
                Node.DOCUMENT_TYPE_NODE,
                Node.PROCESSING_INSTRUCTION_NODE,
            ):
                return node

    want = want.strip().replace('\\n', '\n')
    got = got.strip().replace('\\n', '\n')

    # If the string is not a complete xml document, we may need to add a
    # root element. This allow us to compare fragments, like "<foo/><bar/>"
    if not want.startswith('<?xml'):
        wrapper = '<root>%s</root>'
        want = wrapper % want
        got = wrapper % got

    # Parse the want and got strings, and compare the parsings.
    want_root = first_node(parseString(want))
    got_root = first_node(parseString(got))

    return check_element(want_root, got_root)


class CaptureQueriesContext:
    """
    Context manager that captures queries executed by the specified connection.
    """
    def __init__(self, connection):
        self.connection = connection

    def __iter__(self):
        return iter(self.captured_queries)

    def __getitem__(self, index):
        return self.captured_queries[index]

    def __len__(self):
        return len(self.captured_queries)

    @property
    def captured_queries(self):
        return self.connection.queries[self.initial_queries:self.final_queries]

    def __enter__(self):
        """
        Enter context management, temporarily enabling debug cursor, ensuring connection, and recording initial queries. Returns the instance.
        
        Args:
        self (DatabaseWrapper): The database wrapper instance.
        
        Attributes:
        force_debug_cursor (bool): A flag indicating whether to use the debug cursor.
        connection (Connection): The database connection object.
        initial_queries (int): The number of initial queries recorded.
        final_queries (int): The number of final queries recorded after exiting the context.
        
        Returns:
        Database
        """

        self.force_debug_cursor = self.connection.force_debug_cursor
        self.connection.force_debug_cursor = True
        # Run any initialization queries if needed so that they won't be
        # included as part of the count.
        self.connection.ensure_connection()
        self.initial_queries = len(self.connection.queries_log)
        self.final_queries = None
        request_started.disconnect(reset_queries)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit context manager.
        
        This method is called when exiting the context manager. It restores the `force_debug_cursor` attribute of the connection object to its original value. It also connects the `request_started` signal to the `reset_queries` function. If no exception occurred (`exc_type` is not None), it updates the `final_queries` attribute with the number of queries in the connection's query log.
        
        Args:
        exc_type (type): The type of the exception that was raised,
        """

        self.connection.force_debug_cursor = self.force_debug_cursor
        request_started.connect(reset_queries)
        if exc_type is not None:
            return
        self.final_queries = len(self.connection.queries_log)


class ignore_warnings(TestContextDecorator):
    def __init__(self, **kwargs):
        """
        Initialize the object with keyword arguments.
        
        Args:
        **kwargs: Arbitrary keyword arguments.
        
        Attributes:
        ignore_kwargs (dict): Dictionary of ignored keyword arguments.
        filter_func (function): Function to filter warnings based on the presence of specific keyword arguments.
        
        Summary:
        This method initializes an object with keyword arguments and sets up a warning filter function based on the presence of 'message' or 'module' in the ignored keyword arguments. The filter function is either `warnings.filterwarnings` or
        """

        self.ignore_kwargs = kwargs
        if 'message' in self.ignore_kwargs or 'module' in self.ignore_kwargs:
            self.filter_func = warnings.filterwarnings
        else:
            self.filter_func = warnings.simplefilter
        super().__init__()

    def enable(self):
        """
        Enable warning filtering.
        
        This method sets up warning filtering by temporarily catching all
        warnings using `warnings.catch_warnings()` and then ignoring specific
        warnings based on the provided keyword arguments (`ignore_kwargs`).
        
        Args:
        None
        
        Returns:
        None
        
        Effects:
        - Temporarily catches all warnings using `warnings.catch_warnings()`.
        - Enters the context manager to manage the caught warnings.
        - Ignores specific warnings using `self.filter_func('ignore', **
        """

        self.catch_warnings = warnings.catch_warnings()
        self.catch_warnings.__enter__()
        self.filter_func('ignore', **self.ignore_kwargs)

    def disable(self):
        self.catch_warnings.__exit__(*sys.exc_info())


# On OSes that don't provide tzset (Windows), we can't set the timezone
# in which the program runs. As a consequence, we must skip tests that
# don't enforce a specific timezone (with timezone.override or equivalent),
# or attempt to interpret naive datetimes in the default timezone.

requires_tz_support = skipUnless(
    TZ_SUPPORT,
    "This test relies on the ability to run a program in an arbitrary "
    "time zone, but your operating system isn't able to do that."
)


@contextmanager
def extend_sys_path(*paths):
    """Context manager to temporarily add paths to sys.path."""
    _orig_sys_path = sys.path[:]
    sys.path.extend(paths)
    try:
        yield
    finally:
        sys.path = _orig_sys_path


@contextmanager
def isolate_lru_cache(lru_cache_object):
    """Clear the cache of an LRU cache object on entering and exiting."""
    lru_cache_object.cache_clear()
    try:
        yield
    finally:
        lru_cache_object.cache_clear()


@contextmanager
def captured_output(stream_name):
    """Return a context manager used by captured_stdout/stdin/stderr
    that temporarily replaces the sys stream *stream_name* with a StringIO.

    Note: This function and the following ``captured_std*`` are copied
          from CPython's ``test.support`` module."""
    orig_stdout = getattr(sys, stream_name)
    setattr(sys, stream_name, StringIO())
    try:
        yield getattr(sys, stream_name)
    finally:
        setattr(sys, stream_name, orig_stdout)


def captured_stdout():
    """Capture the output of sys.stdout:

       with captured_stdout() as stdout:
           print("hello")
       self.assertEqual(stdout.getvalue(), "hello\n")
    """
    return captured_output("stdout")


def captured_stderr():
    """Capture the output of sys.stderr:

       with captured_stderr() as stderr:
           print("hello", file=sys.stderr)
       self.assertEqual(stderr.getvalue(), "hello\n")
    """
    return captured_output("stderr")


def captured_stdin():
    """Capture the input to sys.stdin:

       with captured_stdin() as stdin:
           stdin.write('hello\n')
           stdin.seek(0)
           # call test code that consumes from sys.stdin
           captured = input()
       self.assertEqual(captured, "hello")
    """
    return captured_output("stdin")


@contextmanager
def freeze_time(t):
    """
    Context manager to temporarily freeze time.time(). This temporarily
    modifies the time function of the time module. Modules which import the
    time function directly (e.g. `from time import time`) won't be affected
    This isn't meant as a public API, but helps reduce some repetitive code in
    Django's test suite.
    """
    _real_time = time.time
    time.time = lambda: t
    try:
        yield
    finally:
        time.time = _real_time


def require_jinja2(test_func):
    """
    Decorator to enable a Jinja2 template engine in addition to the regular
    Django template engine for a test or skip it if Jinja2 isn't available.
    """
    test_func = skipIf(jinja2 is None, "this test requires jinja2")(test_func)
    return override_settings(TEMPLATES=[{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    }, {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'APP_DIRS': True,
        'OPTIONS': {'keep_trailing_newline': True},
    }])(test_func)


class override_script_prefix(TestContextDecorator):
    """Decorator or context manager to temporary override the script prefix."""
    def __init__(self, prefix):
        self.prefix = prefix
        super().__init__()

    def enable(self):
        self.old_prefix = get_script_prefix()
        set_script_prefix(self.prefix)

    def disable(self):
        set_script_prefix(self.old_prefix)


class LoggingCaptureMixin:
    """
    Capture the output from the 'django' logger and store it on the class's
    logger_output attribute.
    """
    def setUp(self):
        """
        Sets up a logger for testing purposes.
        
        This method configures the Django logger by redirecting its output to an in-memory stream (StringIO). It stores the original stream handler, replaces it with a new one that writes to the StringIO object, and captures any log messages generated during tests.
        
        Args:
        None
        
        Returns:
        None
        
        Attributes:
        self.logger (logging.Logger): The Django logger instance.
        self.old_stream (io.TextIOWrapper): The original stream
        """

        self.logger = logging.getLogger('django')
        self.old_stream = self.logger.handlers[0].stream
        self.logger_output = StringIO()
        self.logger.handlers[0].stream = self.logger_output

    def tearDown(self):
        self.logger.handlers[0].stream = self.old_stream


class isolate_apps(TestContextDecorator):
    """
    Act as either a decorator or a context manager to register models defined
    in its wrapped context to an isolated registry.

    The list of installed apps the isolated registry should contain must be
    passed as arguments.

    Two optional keyword arguments can be specified:

    `attr_name`: attribute assigned the isolated registry if used as a class
                 decorator.

    `kwarg_name`: keyword argument passing the isolated registry if used as a
                  function decorator.
    """
    def __init__(self, *installed_apps, **kwargs):
        self.installed_apps = installed_apps
        super().__init__(**kwargs)

    def enable(self):
        """
        Enables a set of default applications.
        
        This method saves the current default applications, creates a new set of applications from the installed ones, and updates the default applications with these new settings.
        
        Args:
        self: The instance of the class containing the methods and attributes.
        
        Returns:
        apps: A new set of default applications created from the installed ones.
        
        Attributes modified:
        old_apps: The previous set of default applications.
        default_apps: Updated to the new set of default applications
        """

        self.old_apps = Options.default_apps
        apps = Apps(self.installed_apps)
        setattr(Options, 'default_apps', apps)
        return apps

    def disable(self):
        setattr(Options, 'default_apps', self.old_apps)


def tag(*tags):
    """Decorator to add tags to a test class or method."""
    def decorator(obj):
        """
        Decorator function that adds tags to an object.
        
        This function takes an object and a set of tags as input. It checks if the object already has a 'tags' attribute. If it does, it updates the existing set of tags by performing a union with the new tags. If the object does not have a 'tags' attribute, it creates one and assigns it the new tags as a set.
        
        Args:
        obj (object): The object to which tags will be added.
        tags
        """

        if hasattr(obj, 'tags'):
            obj.tags = obj.tags.union(tags)
        else:
            setattr(obj, 'tags', set(tags))
        return obj
    return decorator


@contextmanager
def register_lookup(field, *lookups, lookup_name=None):
    """
    Context manager to temporarily register lookups on a model field using
    lookup_name (or the lookup's lookup_name if not provided).
    """
    try:
        for lookup in lookups:
            field.register_lookup(lookup, lookup_name)
        yield
    finally:
        for lookup in lookups:
            field._unregister_lookup(lookup, lookup_name)
