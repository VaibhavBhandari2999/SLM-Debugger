import functools
import itertools
import logging
import os
import pathlib
import signal
import subprocess
import sys
import threading
import time
import traceback
import weakref
from collections import defaultdict
from pathlib import Path
from types import ModuleType
from zipimport import zipimporter

from django.apps import apps
from django.core.signals import request_finished
from django.dispatch import Signal
from django.utils.functional import cached_property
from django.utils.version import get_version_tuple

autoreload_started = Signal()
file_changed = Signal(providing_args=['file_path', 'kind'])

DJANGO_AUTORELOAD_ENV = 'RUN_MAIN'

logger = logging.getLogger('django.utils.autoreload')

# If an error is raised while importing a file, it's not placed in sys.modules.
# This means that any future modifications aren't caught. Keep a list of these
# file paths to allow watching them in the future.
_error_files = []
_exception = None

try:
    import termios
except ImportError:
    termios = None


try:
    import pywatchman
except ImportError:
    pywatchman = None


def check_errors(fn):
    """
    This function is a decorator that wraps another function (fn) and catches any exceptions raised during its execution. If an exception occurs, it stores the exception information in a global variable `_exception` and appends the filename of the error to a list `_error_files`. The original function's behavior is preserved using `functools.wraps`.
    
    Args:
    fn (function): The function to be wrapped.
    
    Returns:
    function: A wrapped version of the input function that handles exceptions.
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        """
        wrapper(*args, **kwargs) -> None
        
        This function acts as a wrapper around another function `fn`. It catches any exceptions raised by `fn` and stores the exception information in the global variable `_exception`. If the exception does not have a `filename` attribute, it extracts the filename from the traceback. The function then checks if the filename is already in the list `_error_files`, and if not, appends it. Finally, it re-raises the exception.
        
        Args:
        """

        global _exception
        try:
            fn(*args, **kwargs)
        except Exception:
            _exception = sys.exc_info()

            et, ev, tb = _exception

            if getattr(ev, 'filename', None) is None:
                # get the filename from the last item in the stack
                filename = traceback.extract_tb(tb)[-1][0]
            else:
                filename = ev.filename

            if filename not in _error_files:
                _error_files.append(filename)

            raise

    return wrapper


def raise_last_exception():
    """
    Raise the last exception that occurred.
    
    This function retrieves the last exception stored in the global variable `_exception` and raises it. The exception is raised with its original traceback, allowing for debugging purposes.
    
    Args:
    None
    
    Returns:
    None
    
    Raises:
    The last exception that occurred, which can be any type of exception (e.g., ValueError, TypeError, etc.).
    
    Global Variables:
    _exception: A tuple containing the exception instance, the exception message, and the
    """

    global _exception
    if _exception is not None:
        raise _exception[0](_exception[1]).with_traceback(_exception[2])


def ensure_echo_on():
    """
    Ensure that echo mode is enabled. Some tools such as PDB disable
    it which causes usability issues after reload.
    """
    if not termios or not sys.stdin.isatty():
        return
    attr_list = termios.tcgetattr(sys.stdin)
    if not attr_list[3] & termios.ECHO:
        attr_list[3] |= termios.ECHO
        if hasattr(signal, 'SIGTTOU'):
            old_handler = signal.signal(signal.SIGTTOU, signal.SIG_IGN)
        else:
            old_handler = None
        termios.tcsetattr(sys.stdin, termios.TCSANOW, attr_list)
        if old_handler is not None:
            signal.signal(signal.SIGTTOU, old_handler)


def iter_all_python_module_files():
    """
    Iterates over all Python module files.
    
    Args:
    None
    
    Returns:
    An iterator over tuples containing (module, file_path).
    
    Summary:
    This function creates a sorted list of modules based on their names,
    filters out weak references, and then calls `iter_modules_and_files`
    with the filtered modules and a set of error files.
    """

    # This is a hot path during reloading. Create a stable sorted list of
    # modules based on the module name and pass it to iter_modules_and_files().
    # This ensures cached results are returned in the usual case that modules
    # aren't loaded on the fly.
    keys = sorted(sys.modules)
    modules = tuple(m for m in map(sys.modules.__getitem__, keys) if not isinstance(m, weakref.ProxyTypes))
    return iter_modules_and_files(modules, frozenset(_error_files))


@functools.lru_cache(maxsize=1)
def iter_modules_and_files(modules, extra_files):
    """Iterate through all modules needed to be watched."""
    sys_file_paths = []
    for module in modules:
        # During debugging (with PyDev) the 'typing.io' and 'typing.re' objects
        # are added to sys.modules, however they are types not modules and so
        # cause issues here.
        if not isinstance(module, ModuleType) or getattr(module, '__spec__', None) is None:
            continue
        spec = module.__spec__
        # Modules could be loaded from places without a concrete location. If
        # this is the case, skip them.
        if spec.has_location:
            origin = spec.loader.archive if isinstance(spec.loader, zipimporter) else spec.origin
            sys_file_paths.append(origin)

    results = set()
    for filename in itertools.chain(sys_file_paths, extra_files):
        if not filename:
            continue
        path = pathlib.Path(filename)
        if not path.exists():
            # The module could have been removed, don't fail loudly if this
            # is the case.
            continue
        results.add(path.resolve().absolute())
    return frozenset(results)


@functools.lru_cache(maxsize=1)
def common_roots(paths):
    """
    Return a tuple of common roots that are shared between the given paths.
    File system watchers operate on directories and aren't cheap to create.
    Try to find the minimum set of directories to watch that encompass all of
    the files that need to be watched.
    """
    # Inspired from Werkzeug:
    # https://github.com/pallets/werkzeug/blob/7477be2853df70a022d9613e765581b9411c3c39/werkzeug/_reloader.py
    # Create a sorted list of the path components, longest first.
    path_parts = sorted([x.parts for x in paths], key=len, reverse=True)
    tree = {}
    for chunks in path_parts:
        node = tree
        # Add each part of the path to the tree.
        for chunk in chunks:
            node = node.setdefault(chunk, {})
        # Clear the last leaf in the tree.
        node.clear()

    # Turn the tree into a list of Path instances.
    def _walk(node, path):
        """
        Walks through a nested dictionary structure, yielding paths to empty nodes.
        
        Args:
        node (dict): The nested dictionary to traverse.
        path (tuple): The current path in the dictionary.
        
        Yields:
        Path: An instance of the Path class representing the path to an empty node.
        
        This function recursively traverses a nested dictionary, collecting paths to nodes that are empty (i.e., dictionaries with no items). It uses the `yield from` syntax to delegate the iteration to
        """

        for prefix, child in node.items():
            yield from _walk(child, path + (prefix,))
        if not node:
            yield Path(*path)

    return tuple(_walk(tree, ()))


def sys_path_directories():
    """
    Yield absolute directories from sys.path, ignoring entries that don't
    exist.
    """
    for path in sys.path:
        path = Path(path)
        if not path.exists():
            continue
        path = path.resolve().absolute()
        # If the path is a file (like a zip file), watch the parent directory.
        if path.is_file():
            yield path.parent
        else:
            yield path


def get_child_arguments():
    """
    Return the executable. This contains a workaround for Windows if the
    executable is reported to not have the .exe extension which can cause bugs
    on reloading.
    """
    import django.__main__

    args = [sys.executable] + ['-W%s' % o for o in sys.warnoptions]
    if sys.argv[0] == django.__main__.__file__:
        # The server was started with `python -m django runserver`.
        args += ['-m', 'django']
        args += sys.argv[1:]
    else:
        args += sys.argv
    return args


def trigger_reload(filename):
    logger.info('%s changed, reloading.', filename)
    sys.exit(3)


def restart_with_reloader():
    """
    Restart the current process with the given child arguments using a reloader loop.
    
    This function creates a new environment with the DJANGO_AUTORELOAD_ENV set to 'true' and then calls the `subprocess.call` method with the provided arguments. The function runs in an infinite loop, restarting the process whenever the exit code is not equal to 3. The important functions used are `os.environ`, `get_child_arguments()`, and `subprocess.call`.
    
    Args:
    None
    """

    new_environ = {**os.environ, DJANGO_AUTORELOAD_ENV: 'true'}
    args = get_child_arguments()
    while True:
        exit_code = subprocess.call(args, env=new_environ, close_fds=False)
        if exit_code != 3:
            return exit_code


class BaseReloader:
    def __init__(self):
        """
        Initialize the object with an empty set of extra files, a dictionary to store directory globs and their associated files, and a stop condition event. This method does not take any parameters and does not return any value.
        
        Attributes:
        extra_files (set): A set containing extra files.
        directory_globs (defaultdict(set)): A dictionary where keys are directory globs and values are sets of associated files.
        _stop_condition (threading.Event): An event object used to signal the stop
        """

        self.extra_files = set()
        self.directory_globs = defaultdict(set)
        self._stop_condition = threading.Event()

    def watch_dir(self, path, glob):
        """
        Watch a directory for changes.
        
        Args:
        path (Path): The absolute path of the directory to watch.
        glob (str): A pattern to match files within the directory.
        
        Raises:
        ValueError: If the provided path is not absolute.
        
        Summary:
        This function watches a specified directory for changes using the given glob pattern. It ensures that the provided path is absolute and logs the action. The directory globs are stored in an internal dictionary for tracking.
        """

        path = Path(path)
        if not path.is_absolute():
            raise ValueError('%s must be absolute.' % path)
        logger.debug('Watching dir %s with glob %s.', path, glob)
        self.directory_globs[path].add(glob)

    def watch_file(self, path):
        """
        Watch a file at the specified path.
        
        Args:
        path (str): The absolute path of the file to watch.
        
        Raises:
        ValueError: If the provided path is not absolute.
        
        Side Effects:
        - Adds the watched file path to the set of extra files being monitored.
        - Logs a debug message indicating that the file is being watched.
        """

        path = Path(path)
        if not path.is_absolute():
            raise ValueError('%s must be absolute.' % path)
        logger.debug('Watching file %s.', path)
        self.extra_files.add(path)

    def watched_files(self, include_globs=True):
        """
        Yield all files that need to be watched, including module files and
        files within globs.
        """
        yield from iter_all_python_module_files()
        yield from self.extra_files
        if include_globs:
            for directory, patterns in self.directory_globs.items():
                for pattern in patterns:
                    yield from directory.glob(pattern)

    def wait_for_apps_ready(self, app_reg, django_main_thread):
        """
        Wait until Django reports that the apps have been loaded. If the given
        thread has terminated before the apps are ready, then a SyntaxError or
        other non-recoverable error has been raised. In that case, stop waiting
        for the apps_ready event and continue processing.

        Return True if the thread is alive and the ready event has been
        triggered, or False if the thread is terminated while waiting for the
        event.
        """
        while django_main_thread.is_alive():
            if app_reg.ready_event.wait(timeout=0.1):
                return True
        else:
            logger.debug('Main Django thread has terminated before apps are ready.')
            return False

    def run(self, django_main_thread):
        """
        Waits for applications to be ready, accesses the URL resolver module, and starts the autoreload loop.
        
        Args:
        self: The instance of the class containing this method.
        django_main_thread: The main thread of the Django application.
        
        Summary:
        This function waits for the applications to be ready using the `wait_for_apps_ready` method, accesses the URL resolver module using `get_resolver().urlconf_module`, and sends an `autoreload_started` signal before starting the
        """

        logger.debug('Waiting for apps ready_event.')
        self.wait_for_apps_ready(apps, django_main_thread)
        from django.urls import get_resolver
        # Prevent a race condition where URL modules aren't loaded when the
        # reloader starts by accessing the urlconf_module property.
        try:
            get_resolver().urlconf_module
        except Exception:
            # Loading the urlconf can result in errors during development.
            # If this occurs then swallow the error and continue.
            pass
        logger.debug('Apps ready_event triggered. Sending autoreload_started signal.')
        autoreload_started.send(sender=self)
        self.run_loop()

    def run_loop(self):
        """
        Runs a loop that continuously ticks until the stop condition is met.
        
        This function generates a ticker using the `tick` method of the current object. It then enters a loop where it continuously calls the `next` function on the ticker generator. If a `StopIteration` exception is raised, the loop breaks. The loop continues until the `should_stop` attribute of the current object becomes True. After the loop exits, the `stop` method of the current object is called.
        
        Args:
        """

        ticker = self.tick()
        while not self.should_stop:
            try:
                next(ticker)
            except StopIteration:
                break
        self.stop()

    def tick(self):
        """
        This generator is called in a loop from run_loop. It's important that
        the method takes care of pausing or otherwise waiting for a period of
        time. This split between run_loop() and tick() is to improve the
        testability of the reloader implementations by decoupling the work they
        do from the loop.
        """
        raise NotImplementedError('subclasses must implement tick().')

    @classmethod
    def check_availability(cls):
        raise NotImplementedError('subclasses must implement check_availability().')

    def notify_file_changed(self, path):
        """
        Notifies the specified file has been changed. Sends a signal to registered listeners with the file path as an argument. Logs the notification and checks if any listener responded. If no listener responded, triggers a file reload.
        
        Args:
        path (str): The file path that has been changed.
        
        Returns:
        None
        
        Signal:
        file_changed: Sent when a file is changed, with the file path as the sender and the file path as an argument.
        
        Logging:
        Logs the
        """

        results = file_changed.send(sender=self, file_path=path)
        logger.debug('%s notified as changed. Signal results: %s.', path, results)
        if not any(res[1] for res in results):
            trigger_reload(path)

    # These are primarily used for testing.
    @property
    def should_stop(self):
        return self._stop_condition.is_set()

    def stop(self):
        self._stop_condition.set()


class StatReloader(BaseReloader):
    SLEEP_TIME = 1  # Check for changes once per second.

    def tick(self):
        """
        Tick method for monitoring file changes.
        
        This method continuously checks the modification times of files specified by `snapshot_files` method. It updates the `mtimes` dictionary with the latest modification times and notifies when a file's modification time changes.
        
        Args:
        None
        
        Returns:
        None
        
        Yields:
        None
        
        Important Functions:
        - `snapshot_files`: Provides the file paths and their modification times.
        - `logger.debug`: Logs debug messages about file changes and first
        """

        mtimes = {}
        while True:
            for filepath, mtime in self.snapshot_files():
                old_time = mtimes.get(filepath)
                if old_time is None:
                    logger.debug('File %s first seen with mtime %s', filepath, mtime)
                    mtimes[filepath] = mtime
                    continue
                elif mtime > old_time:
                    logger.debug('File %s previous mtime: %s, current mtime: %s', filepath, old_time, mtime)
                    self.notify_file_changed(filepath)

            time.sleep(self.SLEEP_TIME)
            yield

    def snapshot_files(self):
        """
        Generates a snapshot of files being watched by the object. Yields each file along with its modification time (mtime). The function ensures that no duplicate files are yielded by maintaining a set of seen files. It handles missing files by catching `OSError` exceptions.
        
        Args:
        None
        
        Yields:
        Tuple[Path, float]: A tuple containing the file path and its modification time.
        """

        # watched_files may produce duplicate paths if globs overlap.
        seen_files = set()
        for file in self.watched_files():
            if file in seen_files:
                continue
            try:
                mtime = file.stat().st_mtime
            except OSError:
                # This is thrown when the file does not exist.
                continue
            seen_files.add(file)
            yield file, mtime

    @classmethod
    def check_availability(cls):
        return True


class WatchmanUnavailable(RuntimeError):
    pass


class WatchmanReloader(BaseReloader):
    def __init__(self):
        """
        Initialize WatchmanClient with default settings.
        
        Args:
        None
        
        Attributes:
        roots (defaultdict): Stores the roots of monitored directories.
        processed_request (threading.Event): Event to indicate if a request has been processed.
        client_timeout (int): Timeout value for client requests, defaults to 5 seconds based on environment variable DJANGO_WATCHMAN_TIMEOUT.
        
        Returns:
        None
        """

        self.roots = defaultdict(set)
        self.processed_request = threading.Event()
        self.client_timeout = int(os.environ.get('DJANGO_WATCHMAN_TIMEOUT', 5))
        super().__init__()

    @cached_property
    def client(self):
        return pywatchman.client(timeout=self.client_timeout)

    def _watch_root(self, root):
        """
        Watches the specified root directory using Watchman.
        
        Args:
        root (Path): The root directory to watch.
        
        Returns:
        tuple: A tuple containing the watch key and relative path returned by Watchman, or None if the root does not exist or its parent cannot be found.
        
        Notes:
        - This function checks if the root directory exists. If it doesn't, it tries to watch the parent directory instead.
        - If both the root and its parent do not exist,
        """

        # In practice this shouldn't occur, however, it's possible that a
        # directory that doesn't exist yet is being watched. If it's outside of
        # sys.path then this will end up a new root. How to handle this isn't
        # clear: Not adding the root will likely break when subscribing to the
        # changes, however, as this is currently an internal API,  no files
        # will be being watched outside of sys.path. Fixing this by checking
        # inside watch_glob() and watch_dir() is expensive, instead this could
        # could fall back to the StatReloader if this case is detected? For
        # now, watching its parent, if possible, is sufficient.
        if not root.exists():
            if not root.parent.exists():
                logger.warning('Unable to watch root dir %s as neither it or its parent exist.', root)
                return
            root = root.parent
        result = self.client.query('watch-project', str(root.absolute()))
        if 'warning' in result:
            logger.warning('Watchman warning: %s', result['warning'])
        logger.debug('Watchman watch-project result: %s', result)
        return result['watch'], result.get('relative_path')

    @functools.lru_cache()
    def _get_clock(self, root):
        return self.client.query('clock', root)['clock']

    def _subscribe(self, directory, name, expression):
        """
        Subscribe to changes in a specified directory using Watchman.
        
        Args:
        directory (str): The directory to monitor for changes.
        name (str): A unique name for the subscription.
        expression (str): The Watchman expression to filter the results.
        
        Returns:
        None
        
        Summary:
        This function initiates a subscription to changes in a specified directory using the Watchman tool. It constructs a query with the given expression and optional relative path, then sends the subscription request to Watch
        """

        root, rel_path = self._watch_root(directory)
        query = {
            'expression': expression,
            'fields': ['name'],
            'since': self._get_clock(root),
            'dedup_results': True,
        }
        if rel_path:
            query['relative_root'] = rel_path
        logger.debug('Issuing watchman subscription %s, for root %s. Query: %s', name, root, query)
        self.client.query('subscribe', root, name, query)

    def _subscribe_dir(self, directory, filenames):
        """
        Subscribe to changes in a directory or its parent.
        
        Args:
        directory (Path): The directory to subscribe to.
        filenames (List[str]): List of filenames to monitor within the directory.
        
        Returns:
        None
        
        Summary:
        This function subscribes to changes in a specified directory or its parent directory. It checks if the directory exists, and if not, it creates a subscription for the parent directory with a specific prefix and file names. If the directory exists, it creates a subscription
        """

        if not directory.exists():
            if not directory.parent.exists():
                logger.warning('Unable to watch directory %s as neither it or its parent exist.', directory)
                return
            prefix = 'files-parent-%s' % directory.name
            filenames = ['%s/%s' % (directory.name, filename) for filename in filenames]
            directory = directory.parent
            expression = ['name', filenames, 'wholename']
        else:
            prefix = 'files'
            expression = ['name', filenames]
        self._subscribe(directory, '%s:%s' % (prefix, directory), expression)

    def _watch_glob(self, directory, patterns):
        """
        Watch a directory with a specific glob. If the directory doesn't yet
        exist, attempt to watch the parent directory and amend the patterns to
        include this. It's important this method isn't called more than one per
        directory when updating all subscriptions. Subsequent calls will
        overwrite the named subscription, so it must include all possible glob
        expressions.
        """
        prefix = 'glob'
        if not directory.exists():
            if not directory.parent.exists():
                logger.warning('Unable to watch directory %s as neither it or its parent exist.', directory)
                return
            prefix = 'glob-parent-%s' % directory.name
            patterns = ['%s/%s' % (directory.name, pattern) for pattern in patterns]
            directory = directory.parent

        expression = ['anyof']
        for pattern in patterns:
            expression.append(['match', pattern, 'wholename'])
        self._subscribe(directory, '%s:%s' % (prefix, directory), expression)

    def watched_roots(self, watched_files):
        """
        Generates a set of directories to watch for file changes.
        
        Args:
        watched_files (list): A list of `Path` objects representing files to be watched.
        
        Returns:
        frozenset: A collection of directories to be monitored, including extra directories from `directory_globs`, directories of the watched files, and system paths from `sys_path_directories`.
        
        Important Functions:
        - `directory_globs`: Provides extra directories to watch.
        - `watched_files`: List
        """

        extra_directories = self.directory_globs.keys()
        watched_file_dirs = [f.parent for f in watched_files]
        sys_paths = list(sys_path_directories())
        return frozenset((*extra_directories, *watched_file_dirs, *sys_paths))

    def _update_watches(self):
        """
        Updates the file watches.
        
        This method updates the file watches based on the currently watched files
        and their common roots. It sets up initial roots for performance, with the
        shortest roots first, and then watches directories using globs. The watched
        files are grouped by their parent directory, and each group is subscribed
        to with relative paths.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `self.watched_files()`: Retrieves the
        """

        watched_files = list(self.watched_files(include_globs=False))
        found_roots = common_roots(self.watched_roots(watched_files))
        logger.debug('Watching %s files', len(watched_files))
        logger.debug('Found common roots: %s', found_roots)
        # Setup initial roots for performance, shortest roots first.
        for root in sorted(found_roots):
            self._watch_root(root)
        for directory, patterns in self.directory_globs.items():
            self._watch_glob(directory, patterns)
        # Group sorted watched_files by their parent directory.
        sorted_files = sorted(watched_files, key=lambda p: p.parent)
        for directory, group in itertools.groupby(sorted_files, key=lambda p: p.parent):
            # These paths need to be relative to the parent directory.
            self._subscribe_dir(directory, [str(p.relative_to(directory)) for p in group])

    def update_watches(self):
        """
        Updates the watches.
        
        This method attempts to update the watches using the `_update_watches` method. If an exception occurs during the update process, it checks the server status using `check_server_status`. If the service is still available, it re-raises the original exception; otherwise, it suppresses the exception.
        
        Args:
        None
        
        Returns:
        None
        """

        try:
            self._update_watches()
        except Exception as ex:
            # If the service is still available, raise the original exception.
            if self.check_server_status(ex):
                raise

    def _check_subscription(self, sub):
        """
        Checks a subscription for results and notifies of file changes.
        
        Args:
        sub (str): The subscription identifier.
        
        Summary:
        This function retrieves a subscription from the client, logs the subscription details, and processes any results. It extracts the root directory from the subscription name and iterates over the files within the subscription, notifying of any file changes.
        
        Returns:
        None
        """

        subscription = self.client.getSubscription(sub)
        if not subscription:
            return
        logger.debug('Watchman subscription %s has results.', sub)
        for result in subscription:
            # When using watch-project, it's not simple to get the relative
            # directory without storing some specific state. Store the full
            # path to the directory in the subscription name, prefixed by its
            # type (glob, files).
            root_directory = Path(result['subscription'].split(':', 1)[1])
            logger.debug('Found root directory %s', root_directory)
            for file in result.get('files', []):
                self.notify_file_changed(root_directory / file)

    def request_processed(self, **kwargs):
        logger.debug('Request processed. Setting update_watches event.')
        self.processed_request.set()

    def tick(self):
        """
        Tick method for processing watchman notifications.
        
        This method continuously checks for new notifications from Watchman and processes them. It connects to the `request_finished` signal, updates watches, and handles subscription checks and errors.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `request_finished.connect(self.request_processed)`
        - `self.update_watches()`
        - `self.client.receive()`
        - `self.check_server_status(ex)`
        
        Variables Affected
        """

        request_finished.connect(self.request_processed)
        self.update_watches()
        while True:
            if self.processed_request.is_set():
                self.update_watches()
                self.processed_request.clear()
            try:
                self.client.receive()
            except pywatchman.SocketTimeout:
                pass
            except pywatchman.WatchmanError as ex:
                logger.debug('Watchman error: %s, checking server status.', ex)
                self.check_server_status(ex)
            else:
                for sub in list(self.client.subs.keys()):
                    self._check_subscription(sub)
            yield

    def stop(self):
        self.client.close()
        super().stop()

    def check_server_status(self, inner_ex=None):
        """Return True if the server is available."""
        try:
            self.client.query('version')
        except Exception:
            raise WatchmanUnavailable(str(inner_ex)) from inner_ex
        return True

    @classmethod
    def check_availability(cls):
        """
        Checks the availability of the Watchman service and its version.
        
        This method verifies that the `pywatchman` library is installed and that the Watchman service is accessible. It also checks the version of Watchman to ensure it meets the minimum requirement of 4.9.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        WatchmanUnavailable: If `pywatchman` is not installed, if the Watchman service cannot be connected to, or if the Watch
        """

        if not pywatchman:
            raise WatchmanUnavailable('pywatchman not installed.')
        client = pywatchman.client(timeout=0.1)
        try:
            result = client.capabilityCheck()
        except Exception:
            # The service is down?
            raise WatchmanUnavailable('Cannot connect to the watchman service.')
        version = get_version_tuple(result['version'])
        # Watchman 4.9 includes multiple improvements to watching project
        # directories as well as case insensitive filesystems.
        logger.debug('Watchman version %s', version)
        if version < (4, 9):
            raise WatchmanUnavailable('Watchman 4.9 or later is required.')


def get_reloader():
    """Return the most suitable reloader for this environment."""
    try:
        WatchmanReloader.check_availability()
    except WatchmanUnavailable:
        return StatReloader()
    return WatchmanReloader()


def start_django(reloader, main_func, *args, **kwargs):
    """
    Starts a Django application using the specified reloader and main function.
    
    Args:
    reloader (object): The reloader object responsible for monitoring file changes.
    main_func (function): The main function to run the Django application.
    *args: Variable length argument list passed to the main function.
    **kwargs: Arbitrary keyword arguments passed to the main function.
    
    Summary:
    This function starts a Django application by running the provided main function in a separate thread. It uses the specified
    """

    ensure_echo_on()

    main_func = check_errors(main_func)
    django_main_thread = threading.Thread(target=main_func, args=args, kwargs=kwargs, name='django-main-thread')
    django_main_thread.setDaemon(True)
    django_main_thread.start()

    while not reloader.should_stop:
        try:
            reloader.run(django_main_thread)
        except WatchmanUnavailable as ex:
            # It's possible that the watchman service shuts down or otherwise
            # becomes unavailable. In that case, use the StatReloader.
            reloader = StatReloader()
            logger.error('Error connecting to Watchman: %s', ex)
            logger.info('Watching for file changes with %s', reloader.__class__.__name__)


def run_with_reloader(main_func, *args, **kwargs):
    """
    Starts the Django development server with automatic reloading.
    
    This function watches for file changes and automatically restarts the server
    when changes are detected. It uses the `get_reloader` function to determine
    the appropriate reloader based on the environment variable `DJANGO_AUTORELOAD_ENV`.
    
    Args:
    main_func (callable): The main function to be executed by the server.
    *args: Variable length argument list passed to `main_func`.
    **kwargs: Arbitrary keyword arguments
    """

    signal.signal(signal.SIGTERM, lambda *args: sys.exit(0))
    try:
        if os.environ.get(DJANGO_AUTORELOAD_ENV) == 'true':
            reloader = get_reloader()
            logger.info('Watching for file changes with %s', reloader.__class__.__name__)
            start_django(reloader, main_func, *args, **kwargs)
        else:
            exit_code = restart_with_reloader()
            sys.exit(exit_code)
    except KeyboardInterrupt:
        pass
