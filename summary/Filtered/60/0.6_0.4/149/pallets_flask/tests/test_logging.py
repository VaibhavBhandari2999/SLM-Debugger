import logging
import sys
from io import StringIO

import pytest

from flask.logging import default_handler
from flask.logging import has_level_handler
from flask.logging import wsgi_errors_stream


@pytest.fixture(autouse=True)
def reset_logging(pytestconfig):
    root_handlers = logging.root.handlers[:]
    logging.root.handlers = []
    root_level = logging.root.level

    logger = logging.getLogger("flask_test")
    logger.handlers = []
    logger.setLevel(logging.NOTSET)

    logging_plugin = pytestconfig.pluginmanager.unregister(name="logging-plugin")

    yield

    logging.root.handlers[:] = root_handlers
    logging.root.setLevel(root_level)

    logger.handlers = []
    logger.setLevel(logging.NOTSET)

    if logging_plugin:
        pytestconfig.pluginmanager.register(logging_plugin, "logging-plugin")


def test_logger(app):
    """
    Function to test the logger configuration of a Flask application.
    
    Parameters:
    app (Flask): The Flask application instance to test.
    
    Returns:
    None: This function asserts the logger configuration and does not return any value.
    
    Key Assertions:
    - The logger's name should be "flask_test".
    - The logger's level should be set to logging.NOTSET.
    - The logger should have one handler, which is the default handler.
    """

    assert app.logger.name == "flask_test"
    assert app.logger.level == logging.NOTSET
    assert app.logger.handlers == [default_handler]


def test_logger_debug(app):
    app.debug = True
    assert app.logger.level == logging.DEBUG
    assert app.logger.handlers == [default_handler]


def test_existing_handler(app):
    """
    Function to test an existing logger handler in a Flask application.
    
    This function adds a StreamHandler to the root logger and checks the logger level and handlers of the provided Flask application.
    
    Parameters:
    app (Flask): The Flask application to test.
    
    Returns:
    None: This function does not return any value. It asserts the logger level and handlers of the provided Flask application.
    """

    logging.root.addHandler(logging.StreamHandler())
    assert app.logger.level == logging.NOTSET
    assert not app.logger.handlers


def test_wsgi_errors_stream(app, client):
    @app.route("/")
    def index():
        app.logger.error("test")
        return ""

    stream = StringIO()
    client.get("/", errors_stream=stream)
    assert "ERROR in test_logging: test" in stream.getvalue()

    assert wsgi_errors_stream._get_current_object() is sys.stderr

    with app.test_request_context(errors_stream=stream):
        assert wsgi_errors_stream._get_current_object() is stream


def test_has_level_handler():
    logger = logging.getLogger("flask.app")
    assert not has_level_handler(logger)

    handler = logging.StreamHandler()
    logging.root.addHandler(handler)
    assert has_level_handler(logger)

    logger.propagate = False
    assert not has_level_handler(logger)
    logger.propagate = True

    handler.setLevel(logging.ERROR)
    assert not has_level_handler(logger)


def test_log_view_exception(app, client):
    """
    Tests the logging of exceptions in the view function.
    
    This function simulates a view function that raises an exception and checks if the exception is properly logged and the response status code is 500. It also verifies that the error message contains the correct information about the exception and the request path.
    
    Parameters:
    app (Flask): The Flask application object.
    client (TestClient): The test client for making requests to the application.
    
    Returns:
    None: This function does not return anything.
    """

    @app.route("/")
    def index():
        raise Exception("test")

    app.testing = False
    stream = StringIO()
    rv = client.get("/", errors_stream=stream)
    assert rv.status_code == 500
    assert rv.data
    err = stream.getvalue()
    assert "Exception on / [GET]" in err
    assert "Exception: test" in err

    assert rv.status_code == 500
    assert rv.data
    err = stream.getvalue()
    assert "Exception on / [GET]" in err
    assert "Exception: test" in err
