from typing import Generator
from typing import Optional
from typing import Union

import pytest
from _pytest._io.saferepr import saferepr
from _pytest.config import Config
from _pytest.config import ExitCode
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureDef
from _pytest.fixtures import SubRequest


def pytest_addoption(parser: Parser) -> None:
    """
    Add options to the pytest command line for controlling the setup and execution of tests.
    
    This function is called by pytest to add custom options to the command line. These options allow users to control the behavior of pytest, specifically focusing on the setup of fixtures.
    
    Parameters:
    parser (Parser): The pytest parser object used to add command line options.
    
    Returns:
    None: This function does not return any value. It modifies the pytest parser object in place.
    
    Key Options:
    --setuponly, --setup
    """

    group = parser.getgroup("debugconfig")
    group.addoption(
        "--setuponly",
        "--setup-only",
        action="store_true",
        help="only setup fixtures, do not execute tests.",
    )
    group.addoption(
        "--setupshow",
        "--setup-show",
        action="store_true",
        help="show setup of fixtures while executing tests.",
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(
    fixturedef: FixtureDef, request: SubRequest
) -> Generator[None, None, None]:
    yield
    if request.config.option.setupshow:
        if hasattr(request, "param"):
            # Save the fixture parameter so ._show_fixture_action() can
            # display it now and during the teardown (in .finish()).
            if fixturedef.ids:
                if callable(fixturedef.ids):
                    param = fixturedef.ids(request.param)
                else:
                    param = fixturedef.ids[request.param_index]
            else:
                param = request.param
            fixturedef.cached_param = param  # type: ignore[attr-defined]
        _show_fixture_action(fixturedef, "SETUP")


def pytest_fixture_post_finalizer(fixturedef: FixtureDef) -> None:
    if fixturedef.cached_result is not None:
        config = fixturedef._fixturemanager.config
        if config.option.setupshow:
            _show_fixture_action(fixturedef, "TEARDOWN")
            if hasattr(fixturedef, "cached_param"):
                del fixturedef.cached_param  # type: ignore[attr-defined]


def _show_fixture_action(fixturedef: FixtureDef, msg: str) -> None:
    """
    Show a fixture action.
    
    This function is used to display a fixture action, such as setup or teardown, in a structured manner. It is typically used in the context of a testing framework where fixtures are managed and their lifecycle is tracked.
    
    Parameters:
    fixturedef (FixtureDef): The fixture definition object containing information about the fixture and its scope.
    msg (str): A message indicating the type of action, such as 'SETUP' or 'TEARDOWN'.
    
    This function does not return any
    """

    config = fixturedef._fixturemanager.config
    capman = config.pluginmanager.getplugin("capturemanager")
    if capman:
        capman.suspend_global_capture()

    tw = config.get_terminal_writer()
    tw.line()
    tw.write(" " * 2 * fixturedef.scopenum)
    tw.write(
        "{step} {scope} {fixture}".format(
            step=msg.ljust(8),  # align the output to TEARDOWN
            scope=fixturedef.scope[0].upper(),
            fixture=fixturedef.argname,
        )
    )

    if msg == "SETUP":
        deps = sorted(arg for arg in fixturedef.argnames if arg != "request")
        if deps:
            tw.write(" (fixtures used: {})".format(", ".join(deps)))

    if hasattr(fixturedef, "cached_param"):
        tw.write("[{}]".format(saferepr(fixturedef.cached_param, maxsize=42)))  # type: ignore[attr-defined]

    tw.flush()

    if capman:
        capman.resume_global_capture()


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config: Config) -> Optional[Union[int, ExitCode]]:
    if config.option.setuponly:
        config.option.setupshow = True
    return None
