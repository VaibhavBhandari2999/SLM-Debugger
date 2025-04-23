import pytest


def pytest_addoption(parser):
    """
    Add options to the pytest command line for controlling the setup and execution of tests.
    
    This function is called by pytest to add custom options to the command line. It allows users to specify whether they want to only set up fixtures without running tests, or to show the setup of fixtures during test execution.
    
    Parameters:
    parser (argparse.ArgumentParser): The pytest command line argument parser.
    
    Options:
    --setuponly, --setup-only:
    Action: store_true
    Help: Only set up fixtures,
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
    Function to handle the setup phase of a pytest fixture.
    
    This function is responsible for executing the setup phase of a pytest fixture. It captures the parameter used for the fixture and stores it for later reference during the teardown phase. If the `setupshow` option is enabled in the pytest configuration, it will display the setup action along with the fixture parameter.
    
    Parameters:
    - fixturedef: The fixture definition object.
    - request: The pytest request object.
    
    Yields:
    - None: The function yields control back
    """

    yield
    if request.config.option.setupshow:
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
    """
    Show a fixture action.
    
    This function is used to display a fixture action, such as setup or teardown, in a structured format. It is typically used in the context of a testing framework where fixtures are managed and executed.
    
    Parameters:
    fixturedef (fixture definition): The fixture definition object containing information about the fixture, including its scope and arguments.
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
        tw.write("[{}]".format(fixturedef.cached_param))

    if capman:
        capman.resume_global_capture()


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config):
    if config.option.setuponly:
        config.option.setupshow = True
