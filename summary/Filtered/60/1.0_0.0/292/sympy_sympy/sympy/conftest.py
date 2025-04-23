import sys
sys._running_pytest = True  # type: ignore
from sympy.external.importtools import version_tuple

import pytest
from sympy.core.cache import clear_cache, USE_CACHE
from sympy.external.gmpy import GROUND_TYPES, HAS_GMPY
from sympy.utilities.misc import ARCH
import re

sp = re.compile(r'([0-9]+)/([1-9][0-9]*)')

def process_split(config, items):
    split = config.getoption("--split")
    if not split:
        return
    m = sp.match(split)
    if not m:
        raise ValueError("split must be a string of the form a/b "
                         "where a and b are ints.")
    i, t = map(int, m.groups())
    start, end = (i-1)*len(items)//t, i*len(items)//t

    if i < t:
        # remove elements from end of list first
        del items[end:]
    del items[:start]


def pytest_report_header(config):
    """
    This function generates a report header for pytest, providing system and library details.
    
    Parameters:
    config (pytest.Config): The pytest configuration object.
    
    Returns:
    str: A string containing the report header with details about the system architecture, cache usage, ground types, and library version if applicable.
    
    Example:
    >>> pytest_report_header(config)
    'architecture: x86_64\ncache: True\nground types: gmpy 2.1.0'
    """

    s = "architecture: %s\n" % ARCH
    s += "cache:        %s\n" % USE_CACHE
    version = ''
    if GROUND_TYPES =='gmpy':
        if HAS_GMPY == 1:
            import gmpy
        elif HAS_GMPY == 2:
            import gmpy2 as gmpy
        version = gmpy.version()
    s += "ground types: %s %s\n" % (GROUND_TYPES, version)
    return s


def pytest_terminal_summary(terminalreporter):
    """
    Function to customize the terminal summary in pytest.
    
    This function is designed to be used as a hook function in pytest. It checks if there are any test cases that have failed or errored. If such cases are found, it writes a warning message to the terminal, indicating that the code should not be committed.
    
    Parameters:
    terminalreporter (TerminalReporter): An instance of TerminalReporter, which provides access to the terminal output and test statistics.
    
    Returns:
    None: This function does not return any
    """

    if (terminalreporter.stats.get('error', None) or
            terminalreporter.stats.get('failed', None)):
        terminalreporter.write_sep(
            ' ', 'DO *NOT* COMMIT!', red=True, bold=True)


def pytest_addoption(parser):
    parser.addoption("--split", action="store", default="",
        help="split tests")


def pytest_collection_modifyitems(config, items):
    """ pytest hook. """
    # handle splits
    process_split(config, items)


@pytest.fixture(autouse=True, scope='module')
def file_clear_cache():
    clear_cache()

@pytest.fixture(autouse=True, scope='module')
def check_disabled(request):
    if getattr(request.module, 'disabled', False):
        pytest.skip("test requirements not met.")
    elif getattr(request.module, 'ipython', False):
        # need to check version and options for ipython tests
        if (version_tuple(pytest.__version__) < version_tuple('2.6.3') and
            pytest.config.getvalue('-s') != 'no'):
            pytest.skip("run py.test with -s or upgrade to newer version.")
