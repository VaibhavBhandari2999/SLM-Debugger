from typing import Optional
from typing import Union

import pytest
from _pytest.config import Config
from _pytest.config import ExitCode
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureDef
from _pytest.fixtures import SubRequest


def pytest_addoption(parser: Parser) -> None:
    group = parser.getgroup("debugconfig")
    group.addoption(
        "--setupplan",
        "--setup-plan",
        action="store_true",
        help="show what fixtures and tests would be executed but "
        "don't execute anything.",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_fixture_setup(
    """
    This function is used to setup pytest fixtures. It checks if the `setupplan` option is provided in the pytest configuration. If it is, it returns a dummy fixture result, otherwise, it returns None. The function takes two parameters: `fixturedef` which is a FixtureDef object representing the fixture to be set up, and `request` which is a SubRequest object representing the request for the fixture. The function returns either a dummy fixture result or None.
    """

    fixturedef: FixtureDef[object], request: SubRequest
) -> Optional[object]:
    # Will return a dummy fixture if the setuponly option is provided.
    if request.config.option.setupplan:
        my_cache_key = fixturedef.cache_key(request)
        fixturedef.cached_result = (None, my_cache_key, None)
        return fixturedef.cached_result
    return None


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config: Config) -> Optional[Union[int, ExitCode]]:
    if config.option.setupplan:
        config.option.setuponly = True
        config.option.setupshow = True
    return None
