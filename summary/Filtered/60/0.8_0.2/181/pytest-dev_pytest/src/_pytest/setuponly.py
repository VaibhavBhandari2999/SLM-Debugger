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
    fixturedef: FixtureDef[object], request: SubRequest
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


def pytest_fixture_post_finalizer(fixturedef: FixtureDef[object]) -> None:
    if fixturedef.cached_result is not None:
        config = fixturedef._fixturemanager.config
        if config.option.setupshow:
            _show_fixture_action(fixturedef, "TEARDOWN")
            if hasattr(fixturedef, "cached_param"):
                del fixturedef.cached_param  # type: ignore[attr-defined]


def _show_fixture_action(fixturedef: FixtureDef[object], msg: str) -> None:
    """
    Show a fixture action.
    
    This function is used to display a message indicating the setup or teardown of a fixture in a testing environment. It aligns the output to indicate the step (SETUP or TEARDOWN), the scope of the fixture, and the name of the fixture. It also handles capturing and un-capturing output based on the configuration.
    
    Parameters:
    fixturedef (FixtureDef): The fixture definition object containing information about the fixture.
    msg (str): The message to display,
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
    """
    This function is invoked by Pytest to handle the command-line interface. It processes the configuration options and returns an exit code or integer.
    
    Parameters:
    config (Config): The pytest configuration object containing various options and settings.
    
    Returns:
    Optional[Union[int, ExitCode]]: The function returns either an integer or an ExitCode object, or None if no specific exit code is defined. If the 'setuponly' option is set, it also sets the 'setupshow' option to True
    """

    if config.option.setuponly:
        config.option.setupshow = True
    return None
