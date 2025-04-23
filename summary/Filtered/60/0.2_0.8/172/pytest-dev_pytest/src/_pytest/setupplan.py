import pytest


def pytest_addoption(parser):
    """
    Function to add command line options for pytest.
    
    This function is designed to be called by pytest to add a custom command line option. It adds an option to show what fixtures and tests would be executed without actually running them.
    
    Parameters:
    parser (argparse.ArgumentParser): The pytest argument parser to which the option will be added.
    
    Returns:
    None: This function does not return anything. It modifies the provided argument parser in place.
    
    Key Parameters:
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
    """
    This function is used to handle the setup of pytest fixtures. If the `setupplan` option is provided, it returns a dummy fixture result, bypassing the actual fixture setup. The function takes two parameters: `fixturedef` which is the definition of the fixture, and `request` which is the pytest request object. The function does not return any value if the `setupplan` option is not provided.
    
    Parameters:
    - fixturedef: The definition of the fixture to be set up.
    -
    """

    # Will return a dummy fixture if the setuponly option is provided.
    if request.config.option.setupplan:
        fixturedef.cached_result = (None, None, None)
        return fixturedef.cached_result


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config):
    if config.option.setupplan:
        config.option.setuponly = True
        config.option.setupshow = True
