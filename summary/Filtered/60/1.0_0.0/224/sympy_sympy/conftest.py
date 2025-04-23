# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import

import os
from itertools import chain
import json
import warnings
import pytest

durations_path = os.path.join(os.path.dirname(__file__), '.ci', 'durations.json')


if os.path.exists(durations_path):
    veryslow_group, slow_group = [list(chain(*[[k+'::'+v for v in files] for k, files in group.items()])) for group
                                  in json.loads(open(durations_path, 'rt').read())]
else:
    warnings.warn("Could not find %s, --quickcheck and --veryquickcheck will have no effect." % durations_path)
    veryslow_group, slow_group = [], []


def pytest_addoption(parser):
    """
    Add command line options for controlling test execution speed.
    
    This function is called by pytest to add custom options to the command line.
    
    Parameters:
    parser (argparse.ArgumentParser): The parser object to which the options will be added.
    
    Options:
    --quickcheck: When set, skips very slow tests.
    --veryquickcheck: When set, skips slow and very slow tests.
    
    Note:
    These options are used to control which tests are run based on their execution time, as determined by `./
    """

    parser.addoption("--quickcheck", dest="runquick", action="store_true",
                     help="Skip very slow tests (see ./ci/parse_durations_log.py)")
    parser.addoption("--veryquickcheck", dest="runveryquick", action="store_true",
                     help="Skip slow & very slow (see ./ci/parse_durations_log.py)")


def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line("markers", "slow: manually marked test as slow (use .ci/durations.json instead)")
    config.addinivalue_line("markers", "quickcheck: skip very slow tests")
    config.addinivalue_line("markers", "veryquickcheck: skip slow & very slow tests")


def pytest_runtest_setup(item):
    """
    Function: pytest_runtest_setup
    
    This function is a pytest hook that runs before each test function is executed. It checks if the current test function is part of the 'veryslow_group' or 'slow_group'. If the test is in 'veryslow_group' and the '--quickcheck' or '--veryquickcheck' command-line options are provided, the test is skipped. Similarly, if the test is in 'slow_group' and the '--veryquickcheck' command-line option is provided,
    """

    if isinstance(item, pytest.Function):
        if item.nodeid in veryslow_group and (item.config.getvalue("runquick") or
                                              item.config.getvalue("runveryquick")):
            pytest.skip("very slow test, skipping since --quickcheck or --veryquickcheck was passed.")
            return
        if item.nodeid in slow_group and item.config.getvalue("runveryquick"):
            pytest.skip("slow test, skipping since --veryquickcheck was passed.")
            return
