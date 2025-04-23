import pytest

from js_example import app


@pytest.fixture(name="app")
def fixture_app():
    """
    fixture_app()
    A testing fixture for an application.
    
    This function sets the testing mode of the application to True, yields the application for testing purposes, and then resets the testing mode to False after the tests are completed.
    
    Parameters:
    None
    
    Yields:
    - app: The application object for testing.
    
    Returns:
    None
    """

    app.testing = True
    yield app
    app.testing = False


@pytest.fixture
def client(app):
    return app.test_client()
