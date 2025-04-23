# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import

import os
from itertools import chain
import json
import sys
import warnings
import pytest
from sympy.utilities.runtests import setup_pprint, _get_doctest_blacklist

durations_path = os.path.join(os.path.dirname(__file__), '.ci', 'durations.json')
blacklist_path = os.path.join(os.path.dirname(__file__), '.ci', 'blacklisted.json')

# Collecting tests from rubi_tests under pytest leads to errors even if the
# tests will be skipped.
collect_ignore = ["sympy/integrals/rubi"] + _get_doctest_blacklist()
if sys.version_info < (3,):
    collect_ignore.append('doc/src/gotchas.rst')

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
    Add command-line options for controlling test execution speed.
    
    This function is called by pytest to add custom options to the command line. It allows users to specify whether they want to run quick tests, very quick tests, or both. Quick tests are those that are not very slow, while very quick tests are those that are not slow or very slow.
    
    Parameters:
    parser (argparse.ArgumentParser): The pytest argument parser to which the options will be added.
    
    Options:
    --quickcheck: If provided,
    """

    parser.addoption("--quickcheck", dest="runquick", action="store_true",
                     help="Skip very slow tests (see ./ci/parse_durations_log.py)")
    parser.addoption("--veryquickcheck", dest="runveryquick", action="store_true",
                     help="Skip slow & very slow (see ./ci/parse_durations_log.py)")


def pytest_configure(config):
    """
    Configure Pytest environment.
    
    This function is called by Pytest during its initialization. It registers additional markers that can be used to mark tests with specific characteristics. These markers can be used to categorize tests based on their speed and execution time requirements.
    
    Parameters:
    config (pytest.Config): The pytest configuration object.
    
    Returns:
    None: This function does not return any value. It modifies the pytest configuration in place.
    """

    # register an additional marker
    config.addinivalue_line("markers", "slow: manually marked test as slow (use .ci/durations.json instead)")
    config.addinivalue_line("markers", "quickcheck: skip very slow tests")
    config.addinivalue_line("markers", "veryquickcheck: skip slow & very slow tests")


def pytest_runtest_setup(item):
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
