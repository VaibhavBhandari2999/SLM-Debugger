# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import

import os
from itertools import chain
import json
import sys
import warnings
import pytest
from sympy.testing.runtests import setup_pprint, _get_doctest_blacklist

durations_path = os.path.join(os.path.dirname(__file__), '.ci', 'durations.json')
blacklist_path = os.path.join(os.path.dirname(__file__), '.ci', 'blacklisted.json')

# Collecting tests from rubi_tests under pytest leads to errors even if the
# tests will be skipped.
collect_ignore = ["sympy/integrals/rubi"] + _get_doctest_blacklist()

# Set up printing for doctests
setup_pprint()
sys.__displayhook__ = sys.displayhook
#from sympy import pprint_use_unicode
#pprint_use_unicode(False)


def _mk_group(group_dict):
    return list(chain(*[[k+'::'+v for v in files] for k, files in group_dict.items()]))

if os.path.exists(durations_path):
    veryslow_group, slow_group = [_mk_group(group_dict) for group_dict in json.loads(open(durations_path, 'rt').read())]
else:
    # warnings in conftest has issues: https://github.com/pytest-dev/pytest/issues/2891
    warnings.warn("conftest.py:22: Could not find %s, --quickcheck and --veryquickcheck will have no effect.\n" % durations_path)
    veryslow_group, slow_group = [], []

if os.path.exists(blacklist_path):
    blacklist_group = _mk_group(json.loads(open(blacklist_path, 'rt').read()))
else:
    warnings.warn("conftest.py:28: Could not find %s, no tests will be skipped due to blacklisting\n" % blacklist_path)
    blacklist_group = []


def pytest_addoption(parser):
    """
    Add command line options for controlling the execution of slow tests.
    
    This function is called by pytest to add custom command line options that allow the user to control which tests are run based on their duration. It adds two options:
    - `--quickcheck`: Skips very slow tests as determined by `./ci/parse_durations_log.py`.
    - `--veryquickcheck`: Skips slow and very slow tests as determined by `./ci/parse_durations_log.py`.
    
    Parameters:
    - parser:
    """

    parser.addoption("--quickcheck", dest="runquick", action="store_true",
                     help="Skip very slow tests (see ./ci/parse_durations_log.py)")
    parser.addoption("--veryquickcheck", dest="runveryquick", action="store_true",
                     help="Skip slow & very slow (see ./ci/parse_durations_log.py)")


def pytest_configure(config):
    """
    Configures the pytest environment by adding custom markers for test categorization.
    
    This function is called during the pytest configuration phase. It registers three custom markers:
    - `slow`: to mark tests as slow, which can be useful for manual identification.
    - `quickcheck`: to skip tests that are considered very slow.
    - `veryquickcheck`: to skip both slow and very slow tests.
    
    Parameters:
    config (pytest.Config): The pytest configuration object.
    
    Returns:
    None: This function does not
    """

    # register an additional marker
    config.addinivalue_line("markers", "slow: manually marked test as slow (use .ci/durations.json instead)")
    config.addinivalue_line("markers", "quickcheck: skip very slow tests")
    config.addinivalue_line("markers", "veryquickcheck: skip slow & very slow tests")


def pytest_runtest_setup(item):
    """
    Function to handle setup for pytest tests.
    
    This function is designed to be used as a pytest hook to manage the setup process for tests. It checks if the current test function is part of a specific group (veryslow_group, slow_group, or blacklist_group) and skips the test if certain conditions are met.
    
    Parameters:
    - item (pytest.Function): The test function being evaluated.
    
    Returns:
    - None: The function does not return anything but may raise a `pytest.skip` exception to skip the test
    """

    if isinstance(item, pytest.Function):
        if item.nodeid in veryslow_group and (item.config.getvalue("runquick") or
                                              item.config.getvalue("runveryquick")):
            pytest.skip("very slow test, skipping since --quickcheck or --veryquickcheck was passed.")
            return
        if item.nodeid in slow_group and item.config.getvalue("runveryquick"):
            pytest.skip("slow test, skipping since --veryquickcheck was passed.")
            return

        if item.nodeid in blacklist_group:
            pytest.skip("blacklisted test, see %s" % blacklist_path)
            return
