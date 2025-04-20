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
    This function is used to handle the setup of pytest fixtures. If the `setupplan` option is provided, it returns a dummy fixture result, bypassing the actual fixture setup. The function takes two parameters: `fixturedef` which is the fixture definition, and `request` which is the pytest request object. It returns the result of the fixture setup, or a dummy result if the `setupplan` option is enabled.
    
    Parameters:
    - fixturedef: The fixture definition object.
    - request:
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
