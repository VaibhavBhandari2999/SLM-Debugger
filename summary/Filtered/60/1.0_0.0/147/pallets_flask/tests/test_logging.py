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
    
    This function is designed to be used as a context manager within pytest tests to temporarily reset the logging configuration. It unregisters the logging plugin, clears the root logger's handlers and level, and then restores the original configuration after the test.
    
    Parameters:
    pytestconfig (pytest.Config): The pytest configuration object.
    
    Yields:
    None: This function does not yield any value but is used as a context manager.
    
    Usage:
    with reset_logging(pytestconfig
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
    app.debug = True
    assert app.logger.level == logging.DEBUG
    assert app.logger.handlers == [default_handler]


def test_existing_handler(app):
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
    """
    Tests whether the specified logger has a level handler.
    
    This function checks if the given logger has a level handler attached to it. It first verifies the absence of a level handler and then adds a StreamHandler to the root logger to check for its presence. It also considers the scenario where the logger's propagate attribute is set to False and the level of the handler is set to a specific level (ERROR in this case).
    
    Parameters:
    logger (logging.Logger): The logger to be checked for a level handler
    """

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
    Tests the logging of an exception view in a Flask application.
    
    This function simulates a GET request to the root route of a Flask application. The root route is decorated to raise an exception. The function then checks the response status code and the content of the error log to ensure that the exception is properly logged.
    
    Parameters:
    app (Flask): The Flask application to test.
    client: The test client for the Flask application.
    
    Returns:
    None: The function asserts conditions and checks the output
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
