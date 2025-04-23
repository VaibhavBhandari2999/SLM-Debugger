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
    Function to add a pytest option for showing the setup plan.
    
    This function is used to extend the pytest command-line interface by adding an option to show the setup plan. The setup plan includes the fixtures and tests that would be executed, but no actual execution takes place.
    
    Parameters:
    parser (Parser): The pytest parser object used to add command-line options.
    
    Returns:
    None: This function does not return any value. It modifies the pytest parser object in place.
    
    Key Parameters:
    --setupplan
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
    if config.option.setupplan:
        config.option.setuponly = True
        config.option.setupshow = True
    return None
