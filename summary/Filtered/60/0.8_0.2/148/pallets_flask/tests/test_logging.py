import logging
import sys
from io import StringIO

import pytest

from flask.logging import default_handler
from flask.logging import has_level_handler
from flask.logging import wsgi_errors_stream


@pytest.fixture(autouse=True)
def reset_logging(pytestconfig):
    """
    Resets the logging configuration for testing purposes.
    
    This function is designed to be used as a context manager to temporarily reset the logging configuration during tests. It unregisters the logging plugin, clears the root logger's handlers and level, and resets the Flask test logger. After the context is exited, it restores the original logging configuration.
    
    Parameters:
    pytestconfig (pytest.Config): The pytest configuration object.
    
    Yields:
    None: This function yields control to the test code within the context.
    
    Usage:
    """

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
    assert app.logger.name == "flask_test"
    assert app.logger.level == logging.NOTSET
    assert app.logger.handlers == [default_handler]


def test_logger_debug(app):
    """
    Configure the application to use debug mode and verify that the logger's level is set to DEBUG and that it has only one handler, which is the default handler.
    
    Parameters:
    app (Flask): The Flask application object to be configured.
    
    Returns:
    None: This function does not return any value. It asserts conditions about the application's debug mode and logger configuration.
    """

    app.debug = True
    assert app.logger.level == logging.DEBUG
    assert app.logger.handlers == [default_handler]


def test_existing_handler(app):
    logging.root.addHandler(logging.StreamHandler())
    assert app.logger.level == logging.NOTSET
    assert not app.logger.handlers


def test_wsgi_errors_stream(app, client):
    """
    Tests the WSGI error stream functionality.
    
    This function checks the behavior of the WSGI error stream when an error is logged in a Flask application. It uses a test client to make a GET request to the root URL and captures the error stream to verify that the error message is logged correctly.
    
    Parameters:
    app (Flask): The Flask application to test.
    client (TestClient): The test client for the Flask application.
    
    Returns:
    None: This function does not return anything.
    """

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
ception on / [GET]" in err
    assert "Exception: test" in err
