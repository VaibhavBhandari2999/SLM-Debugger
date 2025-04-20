from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pytest


def pytest_addoption(parser):
    """
    Function to add options to the pytest configuration.
    
    This function is designed to be called during the setup of pytest. It adds a custom option to the pytest command line interface.
    
    Parameters:
    parser (argparse.ArgumentParser): The pytest argument parser to which the new option will be added.
    
    Returns:
    None: This function does not return any value. It modifies the provided parser in place.
    
    Options:
    --setupplan, --setup-plan: When this option is provided, pytest will show a plan of
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
