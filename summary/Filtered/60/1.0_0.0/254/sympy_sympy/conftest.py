# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import

import os
from itertools import chain
import json
import sys
import warnings
import pytest

durations_path = os.path.join(os.path.dirname(__file__), '.ci', 'durations.json')
blacklist_path = os.path.join(os.path.dirname(__file__), '.ci', 'blacklisted.json')

# Collecting tests from rubi_tests under pytest leads to errors even if the
# tests will be skipped.
collect_ignore = ["sympy/integrals/rubi/rubi_tests"]

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
    parser.addoption("--quickcheck", dest="runquick", action="store_true",
                     help="Skip very slow tests (see ./ci/parse_durations_log.py)")
    parser.addoption("--veryquickcheck", dest="runveryquick", action="store_true",
                     help="Skip slow & very slow (see ./ci/parse_durations_log.py)")


def pytest_configure(config):
    """
    Configure pytest environment.
    
    This function is called by pytest during its initialization. It adds custom markers to the pytest configuration.
    These markers can be used to categorize tests based on their speed and execution requirements.
    
    Parameters:
    config (pytest.Config): The pytest configuration object.
    
    Returns:
    None: This function does not return anything. It modifies the pytest configuration in place.
    """

    # register an additional marker
    config.addinivalue_line("markers", "slow: manually marked test as slow (use .ci/durations.json instead)")
    config.addinivalue_line("markers", "quickcheck: skip very slow tests")
    config.addinivalue_line("markers", "veryquickcheck: skip slow & very slow tests")


def pytest_runtest_setup(item):
    """
    Function to handle test setup for pytest.
    
    This function is designed to be used as a pytest hook to manage the setup of tests. It checks if the test function is part of a specific group (veryslow_group, slow_group, or blacklist_group) and skips the test if certain conditions are met.
    
    Parameters:
    item (pytest.Function): The test function to be checked and potentially skipped.
    
    Returns:
    None: The function does not return anything. It either skips the test or allows it to proceed
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
