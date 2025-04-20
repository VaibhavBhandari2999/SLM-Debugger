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
    """
    Function to handle the setup of pytest fixtures.
    
    This function is responsible for setting up pytest fixtures. If the `setupplan` option is provided, it will return a dummy fixture result without executing the actual setup. The function takes two parameters: `fixturedef` and `request`.
    
    Parameters:
    fixturedef (fixture definition): The definition of the pytest fixture to be set up.
    request (pytest request): The request object representing the test request.
    
    Returns:
    tuple: A tuple containing the result
    """

    # Will return a dummy fixture if the setuponly option is provided.
    if request.config.option.setupplan:
        fixturedef.cached_result = (None, None, None)
        return fixturedef.cached_result


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config):
    """
    pytest_cmdline_main(config)
    
    This function is invoked when pytest starts. It checks if the `setupplan` option is set. If so, it sets the `setuponly` and `setupshow` options to `True`. This function does not return any value but modifies the pytest configuration object in place.
    
    Parameters:
    - config (pytest.Config): The pytest configuration object.
    
    Returns:
    - None: This function modifies the pytest configuration object in place and does not return any value.
    """

    if config.option.setupplan:
        config.option.setuponly = True
        config.option.setupshow = True
