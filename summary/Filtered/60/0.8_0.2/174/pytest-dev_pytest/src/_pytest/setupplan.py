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
    This function is invoked by pytest to handle the command-line interface. If the 'setupplan' option is specified, it sets the 'setuponly' and 'setupshow' options to True. The function does not return any value but modifies the configuration object in place.
    
    Parameters:
    - config: The pytest configuration object.
    
    Key Parameters:
    - config: The pytest configuration object that contains various options and settings.
    
    Keywords:
    - setupplan: A command-line option that, when specified, triggers the function to
    """

    if config.option.setupplan:
        config.option.setuponly = True
        config.option.setupshow = True
