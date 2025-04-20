import pytest

import flask
from flask.globals import app_ctx
from flask.globals import request_ctx


def test_basic_url_generation(app):
    """
    Generate a URL for a given endpoint.
    
    This function tests the generation of a basic URL for a specified endpoint using the Flask framework. It sets the server name and preferred URL scheme in the application configuration. The function then creates a route and generates the URL for that route.
    
    Parameters:
    app (Flask): The Flask application object.
    
    Returns:
    str: The generated URL for the specified endpoint.
    
    Key Details:
    - The server name is set to "localhost".
    - The preferred URL scheme is set
    """

    app.config["SERVER_NAME"] = "localhost"
    app.config["PREFERRED_URL_SCHEME"] = "https"

    @app.route("/")
    def index():
        """
        This function initializes the Flask application context and request context, then asserts that the Werkzeug request environment is properly set. It returns an empty string.
        
        Parameters:
        None
        
        Returns:
        str: An empty string
        
        Context:
        - `app_ctx`: The Flask application context.
        - `request_ctx`: The Flask request context.
        
        Assertions:
        - Ensures that the Werkzeug request environment is not None after the context is set.
        """

        pass

    with app.app_context():
        rv = flask.url_for("index")
        assert rv == "https://localhost/"


def test_url_generation_requires_server_name(app):
    with app.app_context():
        with pytest.raises(RuntimeError):
            flask.url_for("index")


def test_url_generation_without_context_fails():
    with pytest.raises(RuntimeError):
        flask.url_for("index")


def test_request_context_means_app_context(app):
    """
    Tests if the test_request_context context manager provides an application context.
    
    This function checks whether the `test_request_context` context manager correctly sets the application context for the Flask application `app`. It enters the context manager to set the application context and then verifies that the current application object is the same as the input `app`. After exiting the context manager, it confirms that the application context is no longer set.
    
    Parameters:
    app (Flask): The Flask application to test the context manager with.
    
    Returns
    """

    with app.test_request_context():
        assert flask.current_app._get_current_object() is app
    assert not flask.current_app


def test_app_context_provides_current_app(app):
    with app.app_context():
        assert flask.current_app._get_current_object() is app
    assert not flask.current_app


def test_app_tearing_down(app):
    cleanup_stuff = []

    @app.teardown_appcontext
    def cleanup(exception):
        cleanup_stuff.append(exception)

    with app.app_context():
        pass

    assert cleanup_stuff == [None]


def test_app_tearing_down_with_previous_exception(app):
    """
    Function to test application context teardown with previous exceptions.
    
    This function sets up a teardown handler for the application context and then attempts to enter the application context while handling an exception. The teardown handler is expected to capture the exception and not raise it further.
    
    Parameters:
    app (Flask): The Flask application to which the teardown handler is attached.
    
    Returns:
    None: The function does not return a value but modifies the `cleanup_stuff` list to store the exception or None.
    
    Key Points:
    - The
    """

    cleanup_stuff = []

    @app.teardown_appcontext
    def cleanup(exception):
        cleanup_stuff.append(exception)

    try:
        raise Exception("dummy")
    except Exception:
        pass

    with app.app_context():
        pass

    assert cleanup_stuff == [None]


def test_app_tearing_down_with_handled_exception_by_except_block(app):
    cleanup_stuff = []

    @app.teardown_appcontext
    def cleanup(exception):
        cleanup_stuff.append(exception)

    with app.app_context():
        try:
            raise Exception("dummy")
        except Exception:
            pass

    assert cleanup_stuff == [None]


def test_app_tearing_down_with_handled_exception_by_app_handler(app, client):
    app.config["PROPAGATE_EXCEPTIONS"] = True
    cleanup_stuff = []

    @app.teardown_appcontext
    def cleanup(exception):
        cleanup_stuff.append(exception)

    @app.route("/")
    def index():
        raise Exception("dummy")

    @app.errorhandler(Exception)
    def handler(f):
        return flask.jsonify(str(f))

    with app.app_context():
        client.get("/")

    assert cleanup_stuff == [None]


def test_app_tearing_down_with_unhandled_exception(app, client):
    app.config["PROPAGATE_EXCEPTIONS"] = True
    cleanup_stuff = []

    @app.teardown_appcontext
    def cleanup(exception):
        cleanup_stuff.append(exception)

    @app.route("/")
    def index():
        raise ValueError("dummy")

    with pytest.raises(ValueError, match="dummy"):
        with app.app_context():
            client.get("/")

    assert len(cleanup_stuff) == 1
    assert isinstance(cleanup_stuff[0], ValueError)
    assert str(cleanup_stuff[0]) == "dummy"


def test_app_ctx_globals_methods(app, app_ctx):
    """
    This function tests various methods of the global application context (g) in a Flask application. It checks the functionality of getting values, checking for the presence of keys, setting default values, popping values, and iterating over the context. The function operates within the context of a Flask application and its application context.
    
    Parameters:
    app (Flask): The Flask application object.
    app_ctx (Flask.app_context): The application context for the Flask application.
    
    Returns:
    None: This function does not
    """

    # get
    assert flask.g.get("foo") is None
    assert flask.g.get("foo", "bar") == "bar"
    # __contains__
    assert "foo" not in flask.g
    flask.g.foo = "bar"
    assert "foo" in flask.g
    # setdefault
    flask.g.setdefault("bar", "the cake is a lie")
    flask.g.setdefault("bar", "hello world")
    assert flask.g.bar == "the cake is a lie"
    # pop
    assert flask.g.pop("bar") == "the cake is a lie"
    with pytest.raises(KeyError):
        flask.g.pop("bar")
    assert flask.g.pop("bar", "more cake") == "more cake"
    # __iter__
    assert list(flask.g) == ["foo"]
    # __repr__
    assert repr(flask.g) == "<flask.g of 'flask_test'>"


def test_custom_app_ctx_globals_class(app):
    class CustomRequestGlobals:
        def __init__(self):
            self.spam = "eggs"

    app.app_ctx_globals_class = CustomRequestGlobals
    with app.app_context():
        assert flask.render_template_string("{{ g.spam }}") == "eggs"


def test_context_refcounts(app, client):
    """
    This function tests the context reference counting in a Flask application.
    
    Parameters:
    app (Flask): The Flask application instance.
    client (TestClient): The test client for the Flask application.
    
    Returns:
    None: The function asserts that the request and app context teardown functions are called in the correct order.
    
    Key Functions:
    - `teardown_req`: Teardown function for request context.
    - `teardown_app`: Teardown function for application context.
    - `index`: Route handler
    """

    called = []

    @app.teardown_request
    def teardown_req(error=None):
        called.append("request")

    @app.teardown_appcontext
    def teardown_app(error=None):
        called.append("app")

    @app.route("/")
    def index():
        with app_ctx:
            with request_ctx:
                pass

        assert flask.request.environ["werkzeug.request"] is not None
        return ""

    res = client.get("/")
    assert res.status_code == 200
    assert res.data == b""
    assert called == ["request", "app"]


def test_clean_pop(app):
    app.testing = False
    called = []

    @app.teardown_request
    def teardown_req(error=None):
        1 / 0

    @app.teardown_appcontext
    def teardown_app(error=None):
        called.append("TEARDOWN")

    try:
        with app.test_request_context():
            called.append(flask.current_app.name)
    except ZeroDivisionError:
        pass

    assert called == ["flask_test", "TEARDOWN"]
    assert not flask.current_app
