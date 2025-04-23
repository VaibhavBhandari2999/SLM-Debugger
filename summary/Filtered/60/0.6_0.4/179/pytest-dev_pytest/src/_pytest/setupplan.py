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
    Add a custom pytest option to enable a setup plan.
    
    This function is called by pytest to add a custom command-line option. The option allows users to see a plan of which fixtures and tests would be executed without actually running them.
    
    Parameters:
    parser (Parser): The pytest parser object used to add options.
    
    Returns:
    None: This function does not return anything. It modifies the pytest parser object in place.
    
    Key Options:
    --setupplan, --setup-plan: When this option is provided
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
    This function is called by pytest to handle command-line options. It processes the 'setupplan' option and sets 'setuponly' and 'setupshow' options accordingly. If 'setupplan' is provided, 'setuponly' and 'setupshow' are set to True. The function returns None.
    
    Parameters:
    config (Config): The pytest configuration object.
    
    Returns:
    Optional[Union[int, ExitCode]]: None, as the function does not return a value but modifies the configuration object
    """

    if config.option.setupplan:
        config.option.setuponly = True
        config.option.setupshow = True
    return None
