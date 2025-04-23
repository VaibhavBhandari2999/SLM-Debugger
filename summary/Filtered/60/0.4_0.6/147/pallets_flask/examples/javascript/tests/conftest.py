import pytest

from js_example import app


@pytest.fixture(name="app")
def fixture_app():
    """
    fixture_app()
    Generate a test fixture for a Flask application.
    
    This function configures the Flask application to be in testing mode, runs any necessary setup for testing, and yields the application for use in tests. After the tests are completed, the application is reverted to its normal state.
    
    Parameters:
    None
    
    Yields:
    Flask.app: The configured Flask application for testing.
    
    Returns:
    None
    """

    app.testing = True
    yield app
    app.testing = False


@pytest.fixture
def client(app):
    return app.test_client()
