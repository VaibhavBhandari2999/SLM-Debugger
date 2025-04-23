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
    This function is used to handle the setup of pytest fixtures. If the `setupplan` option is provided in the pytest configuration, it returns a dummy fixture result, bypassing the actual fixture setup. The function takes two parameters: `fixturedef` and `request`. The `fixturedef` parameter is a fixture definition object, and the `request` parameter is a request object that provides information about the test request. The function returns the cached result of the fixture, which is set to (None
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
option.setupshow = True
