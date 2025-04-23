import pytest


def pytest_addoption(parser):
    """
    Function to add command line options for pytest.
    
    This function is used to extend the pytest command line options to include
    a flag for showing the setup plan without executing any tests.
    
    Parameters:
    parser (argparse.ArgumentParser): The pytest argument parser object.
    
    Returns:
    None: This function does not return anything. It modifies the provided
    argument parser object in place.
    
    Key Options:
    --setupplan, --setup-plan:
    - Action: store_true
    - Help: Show what fixtures
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
    This function modifies the pytest command-line options. It checks if the `setupplan` option is set. If so, it sets the `setuponly` and `setupshow` options to `True`. This function does not return any value but alters the pytest configuration object.
    
    Parameters:
    - config (pytest.Config): The pytest configuration object.
    
    Key Options:
    - `setupplan`: A command-line option that, when set, triggers the function to modify other options.
    - `setuponly`: When set
    """

    if config.option.setupplan:
        config.option.setuponly = True
        config.option.setupshow = True
