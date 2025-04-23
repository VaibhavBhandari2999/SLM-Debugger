from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys

import pytest


def pytest_addoption(parser):
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
def pytest_fixture_setup(fixturedef, request):
    """
    Function to handle the setup phase of a pytest fixture.
    
    This function is responsible for executing the setup phase of a pytest fixture. It captures the setup phase details and optionally displays them based on the configuration settings. The function yields control to the fixture setup code, and upon completion, it checks if the `setupshow` option is enabled in the pytest configuration. If so, it retrieves the fixture parameter and displays the setup action.
    
    Parameters:
    - fixturedef: The fixture definition object.
    - request: The
    """

    yield
    config = request.config
    if config.option.setupshow:
        if hasattr(request, "param"):
            # Save the fixture parameter so ._show_fixture_action() can
            # display it now and during the teardown (in .finish()).
            if fixturedef.ids:
                if callable(fixturedef.ids):
                    fixturedef.cached_param = fixturedef.ids(request.param)
                else:
                    fixturedef.cached_param = fixturedef.ids[request.param_index]
            else:
                fixturedef.cached_param = request.param
        _show_fixture_action(fixturedef, "SETUP")


def pytest_fixture_post_finalizer(fixturedef):
    """
    This function is a post-finalizer hook for pytest fixtures. It is triggered after the fixture has been used and is being cleaned up. The function checks if the fixture has a cached result, and if so, it retrieves the pytest configuration. If the setupshow option is enabled in the configuration, it calls a helper function to show the fixture action. It also checks if the fixture has a cached parameter and deletes it if present.
    
    Parameters:
    - fixturedef: The fixture definition object containing information about the
    """

    if hasattr(fixturedef, "cached_result"):
        config = fixturedef._fixturemanager.config
        if config.option.setupshow:
            _show_fixture_action(fixturedef, "TEARDOWN")
            if hasattr(fixturedef, "cached_param"):
                del fixturedef.cached_param


def _show_fixture_action(fixturedef, msg):
    config = fixturedef._fixturemanager.config
    capman = config.pluginmanager.getplugin("capturemanager")
    if capman:
        capman.suspend_global_capture()
        out, err = capman.read_global_capture()

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
        tw.write("[{}]".format(fixturedef.cached_param))

    if capman:
        capman.resume_global_capture()
        sys.stdout.write(out)
        sys.stderr.write(err)


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config):
    if config.option.setuponly:
        config.option.setupshow = True
