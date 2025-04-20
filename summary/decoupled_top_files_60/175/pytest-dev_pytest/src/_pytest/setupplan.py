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
    This function is used to handle the setup of pytest fixtures. If the `setupplan` option is provided, it returns a dummy fixture result, bypassing the actual setup process. The function takes two parameters: `fixturedef` and `request`. The `fixturedef` parameter is expected to be a fixture definition, and the `request` parameter is expected to be a pytest request object. The function does not return any value if the `setupplan` option is not provided, but it returns
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
tion.setuponly = True
        config.option.setupshow = True
