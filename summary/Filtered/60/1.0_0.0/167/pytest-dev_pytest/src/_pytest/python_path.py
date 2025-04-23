import sys

import pytest
from pytest import Config
from pytest import Parser


def pytest_addoption(parser: Parser) -> None:
    parser.addini("pythonpath", type="paths", help="Add paths to sys.path", default=[])


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(early_config: Config) -> None:
    """
    Load initial conftests for Pytest.
    
    This function is called early in the Pytest process to modify the Python path. It takes a `Config` object as input and does not return anything. The `Config` object contains information about the configuration of the Pytest session, including the `pythonpath` option, which is a list of paths to be added to `sys.path`.
    
    Parameters:
    early_config (Config): The configuration object for the Pytest session.
    
    The function modifies the `
    """

    # `pythonpath = a b` will set `sys.path` to `[a, b, x, y, z, ...]`
    for path in reversed(early_config.getini("pythonpath")):
        sys.path.insert(0, str(path))


@pytest.hookimpl(trylast=True)
def pytest_unconfigure(config: Config) -> None:
    for path in config.getini("pythonpath"):
        path_str = str(path)
        if path_str in sys.path:
            sys.path.remove(path_str)
