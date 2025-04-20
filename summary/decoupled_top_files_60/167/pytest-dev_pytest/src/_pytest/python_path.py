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
    
    This function is called early in the pytest process to modify the Python path. It takes a `Config` object from pytest as an argument and does not return any value. The function iterates over the `pythonpath` configuration option, reverses the order of the paths, and inserts them at the beginning of `sys.path`.
    
    :param early_config: The pytest configuration object containing the `pythonpath` option.
    :type early_config: Config
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
