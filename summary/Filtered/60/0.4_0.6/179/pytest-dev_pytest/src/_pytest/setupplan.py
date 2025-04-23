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
    fixturedef: FixtureDef, request: SubRequest
) -> Optional[object]:
    # Will return a dummy fixture if the setuponly option is provided.
    if request.config.option.setupplan:
        my_cache_key = fixturedef.cache_key(request)
        fixturedef.cached_result = (None, my_cache_key, None)
        return fixturedef.cached_result
    return None


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config: Config) -> Optional[Union[int, ExitCode]]:
    """
    This function is invoked by Pytest during the command-line execution. It processes the configuration options and modifies them based on the presence of a specific option. If the `setupplan` option is provided, it sets the `setuponly` and `setupshow` options to `True`. The function does not return a value but modifies the configuration in place.
    
    Parameters:
    - config (Config): The Pytest configuration object containing various options and settings.
    
    Returns:
    - None: The function does not return a
    """

    if config.option.setupplan:
        config.option.setuponly = True
        config.option.setupshow = True
    return None
