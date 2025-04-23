import pytest


def pytest_addoption(parser):
    """
    Function to add command line options for pytest.
    
    This function is designed to be called by pytest to add custom command line options. It specifically adds an option to show the setup plan for fixtures and tests without actually running them.
    
    Parameters:
    parser (argparse.ArgumentParser): The pytest argument parser to which the option will be added.
    
    Returns:
    None: This function does not return any value. It modifies the provided parser in place.
    
    Key Options:
    --setupplan, --setup-plan: A boolean
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
    """
    Function to modify pytest command-line options.
    
    This function is designed to be called from the pytest command-line interface. It checks if the `setupplan` option is set. If it is, it sets the `setuponly` and `setupshow` options to `True`. This function does not return any value but modifies the pytest configuration object directly.
    
    Parameters:
    - config (pytest.Config): The pytest configuration object.
    
    Returns:
    - None: The function modifies the pytest configuration object in place and does not
    """

    if config.option.setupplan:
        config.option.setuponly = True
        config.option.setupshow = True
