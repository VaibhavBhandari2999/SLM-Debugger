# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import

import pytest


def pytest_addoption(parser):
    parser.addoption("--slow", dest="runslow", action="store_true",
                     help="allow slow tests to run")


def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line("markers", "slow: slow test")


def pytest_runtest_setup(item):
    """
    Function to conditionally skip slow tests during pytest execution.
    
    This function is designed to be used as a pytest hook to conditionally skip tests marked as 'slow' unless the '--runslow' command-line option is provided.
    
    Parameters:
    item (pytest.Function): The test item to be evaluated.
    
    Returns:
    None: The function does not return anything. It either skips the test or allows it to proceed.
    
    Key Points:
    - The function checks if the test item is of type `pytest.Function`.
    """

    if not isinstance(item, pytest.Function):
        return
    if not item.config.getvalue("runslow") and hasattr(item.obj, 'slow'):
        pytest.skip("slow test: pass --slow to run")
