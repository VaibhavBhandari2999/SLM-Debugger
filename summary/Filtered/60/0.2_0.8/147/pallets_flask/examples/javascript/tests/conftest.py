import pytest

from js_example import app


@pytest.fixture(name="app")
def fixture_app():
    """
    fixture_app()
    Generate a test fixture for a Flask application.
    
    This function sets the testing attribute of the Flask app to True, allowing for testing purposes. It yields the app for use in tests, and then resets the testing attribute to False after the tests are complete.
    
    Parameters:
    None
    
    Yields:
    Flask app: The Flask application for testing.
    
    Returns:
    None
    """

    app.testing = True
    yield app
    app.testing = False


@pytest.fixture
def client(app):
    return app.test_client()
