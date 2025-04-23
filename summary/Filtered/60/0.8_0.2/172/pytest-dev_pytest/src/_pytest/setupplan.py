import pytest


def pytest_addoption(parser):
    """
    Function to add command line options for pytest.
    
    This function is used to extend the pytest command line options to include a
    `--setupplan` or `--setup-plan` flag. This flag, when enabled, will show the
    fixtures and tests that would be executed without actually running them.
    
    Parameters:
    - parser (argparse.ArgumentParser): The pytest argument parser to which the
    new option will be added.
    
    Returns:
    - None: This function does not return any value. It modifies the provided
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
def pytest_fixture_setup(fixturedef, request):
    # Will return a dummy fixture if the setuponly option is provided.
    if request.config.option.setupplan:
        fixturedef.cached_result = (None, None, None)
        return fixturedef.cached_result


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config):
    if config.option.setupplan:
        config.option.setuponly = True
        config.option.setupshow = True
