import sys

import pytest


def pytest_addoption(parser):
    """
    Function to add command line options for pytest.
    
    This function is designed to be called during the setup of pytest to add custom command line options. It specifically adds two options:
    1. `--setuponly` or `--setup-only`: When this flag is set, pytest will only setup the fixtures and will not execute any tests.
    2. `--setupshow` or `--setup-show`: When this flag is set, pytest will show the setup of fixtures while executing the tests.
    
    Parameters:
    -
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
    """
    Setup and Teardown for Pytest Fixtures
    
    This function is responsible for setting up and tearing down pytest fixtures. It captures the setup phase of a fixture, optionally showing the setup details if the `setupshow` configuration option is enabled. The function yields control to the fixture setup code, and upon completion, it checks if the `setupshow` option is active. If so, it retrieves the fixture parameter and displays the setup action. The function also stores the parameter for later use in the teardown
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
