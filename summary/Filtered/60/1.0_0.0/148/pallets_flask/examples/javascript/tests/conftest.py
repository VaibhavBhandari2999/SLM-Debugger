import pytest

from js_example import app


@pytest.fixture(name="app")
def fixture_app():
    """
    fixture_app()
    Generate a test fixture for a Flask application.
    
    This function configures the Flask application for testing by setting the testing mode to True. It yields the application for use in tests. After the tests, the testing mode is reset to False.
    
    Parameters:
    None
    
    Yields:
    flask.app.Flask: The configured Flask application for testing.
    
    Returns:
    None
    """

    app.testing = True
    yield app
    app.testing = False


@pytest.fixture
def client(app):
    return app.test_client()
