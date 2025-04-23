import pytest


def pytest_addoption(parser):
    """
    Function to add command line options for pytest.
    
    This function is used to extend the pytest command line options. It specifically adds an option to show the setup plan for fixtures and tests without executing them.
    
    Parameters:
    - parser (argparse.ArgumentParser): The pytest argument parser to which the new option will be added.
    
    Returns:
    - None: This function does not return any value. It modifies the provided parser object in place.
    
    Key Options:
    - `--setupplan` or `--setup-plan`: A boolean
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
