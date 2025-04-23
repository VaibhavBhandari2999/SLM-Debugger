import pytest


def pytest_addoption(parser):
    """
    Function to add command line options for pytest.
    
    This function is used to extend the pytest command line options. It specifically adds an option to show the setup plan for fixtures and tests without executing them.
    
    Parameters:
    parser (argparse.ArgumentParser): The pytest argument parser to which the new option will be added.
    
    Returns:
    None: This function does not return anything. It modifies the provided parser object in place.
    
    Options:
    --setupplan, --setup-plan: When this option is used, pytest
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
    """
    Function: pytest_fixture_setup
    
    This function is used to handle the setup of a pytest fixture. It checks if the 'setupplan' option is provided in the pytest configuration. If it is, the function returns a dummy fixture result, effectively skipping the actual fixture setup. The function takes two parameters: 'fixturedef' and 'request'. The 'fixturedef' parameter is the fixture definition, and 'request' is the pytest request object. The function does not return any value if the 'setup
    """

    # Will return a dummy fixture if the setuponly option is provided.
    if request.config.option.setupplan:
        fixturedef.cached_result = (None, None, None)
        return fixturedef.cached_result


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config):
    """
    Function to modify pytest command-line options.
    
    This function is designed to be called from the pytest command-line interface. It checks if the `setupplan` option is set. If so, it sets the `setuponly` and `setupshow` options to True. This function does not return any value but modifies the pytest configuration object directly.
    
    Parameters:
    config (pytest.Config): The pytest configuration object.
    
    Returns:
    None: This function modifies the pytest configuration object in place and does not return any
    """

    if config.option.setupplan:
        config.option.setuponly = True
        config.option.setupshow = True
