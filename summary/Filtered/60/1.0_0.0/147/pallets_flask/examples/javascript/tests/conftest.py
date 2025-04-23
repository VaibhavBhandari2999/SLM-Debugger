import pytest

from js_example import app


@pytest.fixture(name="app")
def fixture_app():
    """
    fixture_app()
    A testing fixture for an application.
    
    This function sets the testing attribute of the application to True, yields the application for testing purposes, and then resets the testing attribute to False after the testing is complete.
    
    Parameters:
    None
    
    Yields:
    flask.Flask: The application instance for testing.
    
    Returns:
    None
    """

    app.testing = True
    yield app
    app.testing = False


@pytest.fixture
def client(app):
    return app.test_client()
