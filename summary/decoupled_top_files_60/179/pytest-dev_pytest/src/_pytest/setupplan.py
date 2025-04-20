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
    Generate a Python function that modifies the pytest command-line behavior based on the provided configuration.
    
    This function is designed to be used as a hook function in the pytest framework. It checks if the `setupplan` option is set in the pytest configuration. If `setupplan` is set, it sets the `setuponly` and `setupshow` options to `True`. The function returns `None` to indicate that no exit code is being set.
    
    Parameters:
    config (Config): The pytest configuration
    """

    if config.option.setupplan:
        config.option.setuponly = True
        config.option.setupshow = True
    return None
