import sys
sys._running_pytest = True  # type: ignore
from distutils.version import LooseVersion as V

import pytest
from sympy.core.cache import clear_cache
import re

sp = re.compile(r'([0-9]+)/([1-9][0-9]*)')

def process_split(config, items):
    """
    Splits a list of items based on the provided configuration.
    
    This function processes a list of items and splits it according to the
    configuration options specified. It uses the `--split` option from the
    command-line arguments to determine the split ratio.
    
    Parameters:
    config (object): An object containing the configuration options, including
    the `--split` option.
    items (list): The list of items to be split.
    
    Returns:
    None: The function modifies the `items` list
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
    from sympy.utilities.misc import ARCH
    s = "architecture: %s\n" % ARCH
    from sympy.core.cache import USE_CACHE
    s += "cache:        %s\n" % USE_CACHE
    from sympy.external.gmpy import GROUND_TYPES, HAS_GMPY
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
    """
    Function to check if a test module is disabled or requires specific conditions.
    
    This function checks if the current test module is marked as disabled or if it requires certain conditions to be met, such as a specific version of pytest or the presence of IPython. If the module is disabled or does not meet the required conditions, the test is skipped.
    
    Parameters:
    request (pytest.FixtureRequest): The pytest request object containing metadata about the test.
    
    Returns:
    None: The function does not return any value
    """

    if getattr(request.module, 'disabled', False):
        pytest.skip("test requirements not met.")
    elif getattr(request.module, 'ipython', False):
        # need to check version and options for ipython tests
        if (V(pytest.__version__) < '2.6.3' and
            pytest.config.getvalue('-s') != 'no'):
            pytest.skip("run py.test with -s or upgrade to newer version.")
