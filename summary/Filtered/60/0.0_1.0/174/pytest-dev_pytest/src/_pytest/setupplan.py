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
    Function to handle command-line options for pytest.
    
    This function is designed to be called during the pytest command-line interface initialization. It checks if the `setupplan` option is set. If so, it sets the `setuponly` and `setupshow` options to True, effectively changing the behavior of pytest to only run setup functions and show the plan.
    
    Parameters:
    - config (pytest.Config): The pytest configuration object.
    
    Returns:
    - None: This function does not return any value. It modifies the
    """

    if config.option.setupplan:
        config.option.setuponly = True
        config.option.setupshow = True
onfig.option.setupshow = True
