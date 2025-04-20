import asyncio
import sys

import pytest

from flask import Blueprint
from flask import Flask
from flask import request

pytest.importorskip("asgiref")


class AppError(Exception):
    pass


class BlueprintError(Exception):
    pass


@pytest.fixture(name="async_app")
def _async_app():
    """
    Generate an asynchronous Flask application with routes and error handlers.
    
    This function creates an asynchronous Flask application with multiple routes and error handlers. It includes routes for the main application and a blueprint for additional routes. The application has routes to handle GET and POST requests at the root and '/home' paths. It also includes an error handler for a custom `AppError` and a blueprint with similar functionality.
    
    Parameters:
    - None
    
    Returns:
    - app (Flask): An asynchronous Flask application with defined routes and error
    """

    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    @app.route("/home", methods=["GET", "POST"])
    async def index():
        await asyncio.sleep(0)
        return request.method

    @app.errorhandler(AppError)
    async def handle(_):
        return "", 412

    @app.route("/error")
    async def error():
        raise AppError()

    blueprint = Blueprint("bp", __name__)

    @blueprint.route("/", methods=["GET", "POST"])
    async def bp_index():
        await asyncio.sleep(0)
        return request.method

    @blueprint.errorhandler(BlueprintError)
    async def bp_handle(_):
        return "", 412

    @blueprint.route("/error")
    async def bp_error():
        raise BlueprintError()

    app.register_blueprint(blueprint, url_prefix="/bp")

    return app


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires Python >= 3.7")
@pytest.mark.parametrize("path", ["/", "/home", "/bp/"])
def test_async_route(path, async_app):
    test_client = async_app.test_client()
    response = test_client.get(path)
    assert b"GET" in response.get_data()
    response = test_client.post(path)
    assert b"POST" in response.get_data()


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires Python >= 3.7")
@pytest.mark.parametrize("path", ["/error", "/bp/error"])
def test_async_error_handler(path, async_app):
    """
    Tests the error handling for an asynchronous application.
    
    This function sends a GET request to a specified path using the test client of an asynchronous application. It asserts that the response status code is 412, indicating a precondition failed.
    
    Parameters:
    path (str): The URL path to send the GET request to.
    async_app (FastAPI): The asynchronous FastAPI application instance to test.
    
    Returns:
    None: The function does not return any value but asserts the response status code.
    """

    test_client = async_app.test_client()
    response = test_client.get(path)
    assert response.status_code == 412


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires Python >= 3.7")
def test_async_before_after_request():
    app_first_called = False
    app_before_called = False
    app_after_called = False
    bp_before_called = False
    bp_after_called = False

    app = Flask(__name__)

    @app.route("/")
    def index():
        return ""

    @app.before_first_request
    async def before_first():
        nonlocal app_first_called
        app_first_called = True

    @app.before_request
    async def before():
        nonlocal app_before_called
        app_before_called = True

    @app.after_request
    async def after(response):
        nonlocal app_after_called
        app_after_called = True
        return response

    blueprint = Blueprint("bp", __name__)

    @blueprint.route("/")
    def bp_index():
        return ""

    @blueprint.before_request
    async def bp_before():
        nonlocal bp_before_called
        bp_before_called = True

    @blueprint.after_request
    async def bp_after(response):
        nonlocal bp_after_called
        bp_after_called = True
        return response

    app.register_blueprint(blueprint, url_prefix="/bp")

    test_client = app.test_client()
    test_client.get("/")
    assert app_first_called
    assert app_before_called
    assert app_after_called
    test_client.get("/bp/")
    assert bp_before_called
    assert bp_after_called


@pytest.mark.skipif(sys.version_info >= (3, 7), reason="should only raise Python < 3.7")
def test_async_runtime_error():
    """
    Test asynchronous runtime error.
    
    This function tests the `async_to_sync` method of a Flask application instance to ensure it raises a `RuntimeError` when called with a `None` argument.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    RuntimeError: If the `async_to_sync` method does not raise a `RuntimeError` when called with `None`.
    """

    app = Flask(__name__)
    with pytest.raises(RuntimeError):
        app.async_to_sync(None)
