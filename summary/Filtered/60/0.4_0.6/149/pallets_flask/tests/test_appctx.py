import pytest

import flask
from flask.globals import app_ctx
from flask.globals import request_ctx


def test_basic_url_generation(app):
    """
    Generate a basic URL for a given endpoint in the Flask application.
    
    This function sets up the server name and preferred URL scheme for the Flask application, then generates a URL for the specified endpoint.
    
    Parameters:
    - app (flask.Flask): The Flask application to generate the URL for.
    
    Returns:
    - str: The generated URL for the specified endpoint.
    
    Note:
    - The server name is set to 'localhost'.
    - The preferred URL scheme is set to 'https'.
    - The function uses the `url
    """

    app.config["SERVER_NAME"] = "localhost"
    app.config["PREFERRED_URL_SCHEME"] = "https"

    @app.route("/")
    def index():
        pass

    with app.app_context():
        rv = flask.url_for("index")
        assert rv == "https://localhost/"


def test_url_generation_requires_server_name(app):
    """
    Tests that URL generation requires a server name.
    
    This function ensures that attempting to generate a URL without providing a server name raises a RuntimeError.
    
    Parameters:
    app (Flask): The Flask application context.
    
    Returns:
    None: This function does not return anything. It raises a RuntimeError if the URL generation is attempted without a server name.
    
    Raises:
    RuntimeError: If the URL generation is attempted without a server name.
    """

    with app.app_context():
        with pytest.raises(RuntimeError):
            flask.url_for("index")


def test_url_generation_without_context_fails():
    with pytest.raises(RuntimeError):
        flask.url_for("index")


def test_request_context_means_app_context(app):
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
    Function to test the app teardown behavior with a previous exception.
    
    This function sets up a teardown handler for the application context and then triggers an exception outside of the app context. It then enters the app context and checks if the teardown handler correctly captures the exception.
    
    Parameters:
    app (Flask): The Flask application to test.
    
    Returns:
    None: The function asserts that the teardown handler did not capture the exception, indicating that the teardown was successful in ignoring the previous exception.
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
    """
    This function tests the teardown mechanisms in a Flask application context.
    
    Key Parameters:
    - app: The Flask application instance to test.
    
    This function sets up a Flask application with specific teardown functions and then attempts to run a test request context. It catches any ZeroDivisionError that occurs during the teardown process and asserts that the teardown functions were called in the correct order. It also ensures that the current application context is properly cleared after the teardown.
    
    Returns:
    - None
    """

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
