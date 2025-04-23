from typing import Optional
from typing import Union

import pytest
from _pytest.config import Config
from _pytest.config import ExitCode
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureDef
from _pytest.fixtures import SubRequest


def pytest_addoption(parser: Parser) -> None:
    """
    Add a custom pytest option to enable setup planning.
    
    This function is used to add a custom command-line option to pytest. When this option is enabled, pytest will show which fixtures and tests would be executed without actually running them.
    
    Parameters:
    parser (Parser): The pytest parser object used to register new options.
    
    Returns:
    None: This function does not return any value. It modifies the pytest parser object in place.
    
    Example:
    To use this option, you can add `--setupplan`
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
def pytest_fixture_setup(
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
    """
    Generate a Python function to handle command-line options for pytest.
    
    This function is designed to be used as a command-line main function for pytest. It checks if the `setupplan` option is provided. If so, it sets the `setuponly` and `setupshow` options to `True`. The function returns `None`.
    
    Parameters:
    config (Config): The pytest configuration object.
    
    Returns:
    Optional[Union[int, ExitCode]]: Returns `None` as the function is designed to
    """

    if config.option.setupplan:
        config.option.setuponly = True
        config.option.setupshow = True
    return None
