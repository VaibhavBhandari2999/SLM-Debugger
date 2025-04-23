from __future__ import print_function, division

import sys
sys._running_pytest = True  # type: ignore
from distutils.version import LooseVersion as V

import pytest
from sympy.core.cache import clear_cache
import re

sp = re.compile(r'([0-9]+)/([1-9][0-9]*)')

def process_split(config, items):
    """
    Splits a list of items based on a given configuration.
    
    This function takes a configuration object and a list of items. It uses the
    `--split` option from the configuration to determine how to split the list.
    The `--split` option should be a string in the form 'a/b' where 'a' and 'b' are
    integers. 'a' represents the index of the split and 'b' represents the total
    number of splits. The function will remove elements
    """

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
    Generate a report header for pytest that includes information about the system architecture, use of cache, and ground types.
    
    This function is designed to be used with pytest to provide additional context about the testing environment. It returns a string with details about the system architecture, whether the cache is being used, and the ground types being used for arithmetic operations.
    
    Returns:
    str: A string containing the report header with relevant information.
    """

    from sympy.utilities.misc import ARCH
    s = "architecture: %s\n" % ARCH
    from sympy.core.cache import USE_CACHE
    s += "cache:        %s\n" % USE_CACHE
    from sympy.core.compatibility import GROUND_TYPES, HAS_GMPY
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
    Function to customize the pytest terminal summary.
    
    This function is designed to be used with pytest to modify the terminal summary
    after all tests have been run. It checks if there were any errors or failures
    during the test run and, if so, it writes a warning message to the terminal
    indicating that the code should *not* be committed.
    
    Parameters:
    terminalreporter (pytest_terminal_summary): An instance of the terminal reporter
    from pytest, which provides information about the test run.
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
        if (V(pytest.__version__) < '2.6.3' and
            pytest.config.getvalue('-s') != 'no'):
            pytest.skip("run py.test with -s or upgrade to newer version.")
