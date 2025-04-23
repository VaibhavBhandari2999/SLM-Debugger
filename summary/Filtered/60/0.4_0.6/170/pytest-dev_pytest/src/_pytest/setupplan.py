from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pytest


def pytest_addoption(parser):
    """
    Function to add command-line options for pytest.
    
    This function is designed to be called by pytest to add a custom option for
    showing what fixtures and tests would be executed without actually running
    them. The option is intended to help with debugging and planning test runs.
    
    Parameters:
    parser (argparse.ArgumentParser): The pytest argument parser to which
    the new option will be added.
    
    Returns:
    None: This function does not return any value. It modifies the provided
    argument parser in place
    """

    group = parser.getgroup("debugconfig")
    group.addoption(
        "--setupplan",
        "--setup-plan",
        action="store_true",
        help="show what fixtures and tests would be executed but "
        "don't execute anything.",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_fixture_setup(fixturedef, request):
    # Will return a dummy fixture if the setuponly option is provided.
    if request.config.option.setupplan:
        fixturedef.cached_result = (None, None, None)
        return fixturedef.cached_result


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config):
    if config.option.setupplan:
        config.option.setuponly = True
        config.option.setupshow = True
