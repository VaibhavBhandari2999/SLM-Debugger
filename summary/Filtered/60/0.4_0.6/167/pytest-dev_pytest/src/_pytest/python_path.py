import sys

import pytest
from pytest import Config
from pytest import Parser


def pytest_addoption(parser: Parser) -> None:
    parser.addini("pythonpath", type="paths", help="Add paths to sys.path", default=[])


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(early_config: Config) -> None:
    """
    Load initial conftests for pytest.
    
    This function is called early in the pytest startup process to modify the `sys.path` based on the `pythonpath` configuration option.
    
    Parameters:
    early_config (Config): The pytest configuration object containing the initial configuration details.
    
    Returns:
    None: This function does not return any value. It modifies `sys.path` in place.
    """

    # `pythonpath = a b` will set `sys.path` to `[a, b, x, y, z, ...]`
    for path in reversed(early_config.getini("pythonpath")):
        sys.path.insert(0, str(path))


@pytest.hookimpl(trylast=True)
def pytest_unconfigure(config: Config) -> None:
    """
    Unconfigure pytest environment.
    
    This function is called by pytest at the end of the test run to clean up the environment. It removes any paths specified in the `pythonpath` configuration option from the Python system path (`sys.path`).
    
    Parameters:
    config (Config): The pytest configuration object containing various settings and options.
    
    Returns:
    None: This function does not return any value.
    """

    for path in config.getini("pythonpath"):
        path_str = str(path)
        if path_str in sys.path:
            sys.path.remove(path_str)
