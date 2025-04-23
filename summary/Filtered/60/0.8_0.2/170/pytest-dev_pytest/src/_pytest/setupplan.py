from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pytest


def pytest_addoption(parser):
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
    """
    pytest_cmdline_main(config) -> None
    
    This function is invoked when pytest starts. It checks if the `setupplan` option is set. If so, it sets the `setuponly` and `setupshow` options to True, effectively running only the setup parts of the tests and showing the setup plan.
    
    Parameters:
    - config (pytest.Config): The pytest configuration object.
    
    Returns:
    - None: This function does not return any value.
    """

    if config.option.setupplan:
        config.option.setuponly = True
        config.option.setupshow = True
nfig):
    if config.option.setupplan:
        config.option.setuponly = True
        config.option.setupshow = True
