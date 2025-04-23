from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys

import pytest


def pytest_addoption(parser):
    """
    Add command-line options for pytest to control setup-only execution and detailed setup display.
    
    This function is designed to be called by pytest to add custom options to the command-line interface.
    
    Parameters:
    parser (argparse.ArgumentParser): The pytest argument parser to which the options will be added.
    
    Options:
    --setuponly, --setup-only:
    A boolean flag that, when set, will cause pytest to only setup the fixtures and not execute any tests.
    --setupshow, --setup-show:
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
def pytest_fixture_setup(fixturedef, request):
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
    This function is a post-finalizer hook for pytest fixtures. It is triggered after the execution of a fixture. If the fixture has a cached result, it checks if the `setupshow` option is enabled in the pytest configuration. If it is, it calls `_show_fixture_action` to display the teardown action of the fixture. If the fixture has a cached parameter, it removes it.
    
    Parameters:
    - fixturedef (fixturedef): The fixture definition object that contains information about the fixture.
    
    Returns:
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
ption.setupshow = True
