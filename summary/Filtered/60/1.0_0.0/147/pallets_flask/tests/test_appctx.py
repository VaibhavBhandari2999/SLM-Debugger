import pytest

import flask


def test_basic_url_generation(app):
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
    
    This function checks that attempting to generate a URL using `flask.url_for` without providing a server name raises a `RuntimeError`.
    
    Parameters:
    app (Flask): The Flask application context.
    
    Returns:
    None: This function does not return anything. It raises a `RuntimeError` if the URL generation is not properly constrained.
    
    Raises:
    RuntimeError: If `flask.url_for` is called without a server name in the Flask application context
    """

    with app.app_context():
        with pytest.raises(RuntimeError):
            flask.url_for("index")


def test_url_generation_without_context_fails():
    with pytest.raises(RuntimeError):
        flask.url_for("index")


def test_request_context_means_app_context(app):
    """
    Tests the request context to ensure it correctly sets and removes the application context.
    
    Parameters:
    app (Flask): The Flask application object to test the request context with.
    
    This function checks that the request context correctly sets the current application to the provided Flask app and properly cleans up by removing the application context when the context is exited.
    """

    with app.test_request_context():
        assert flask.current_app._get_current_object() == app
    assert flask._app_ctx_stack.top is None


def test_app_context_provides_current_app(app):
    with app.app_context():
        assert flask.current_app._get_current_object() == app
    assert flask._app_ctx_stack.top is None


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
    Function to test application teardown behavior with previous exceptions.
    
    This function simulates an application context where a teardown function is defined to clean up resources. It raises an exception outside of the application context and then enters the context to trigger the teardown function. The function checks if the teardown function correctly handles the absence of an exception during teardown.
    
    Parameters:
    app (Flask): The Flask application object.
    
    Returns:
    None: The function asserts that the cleanup function appends None to the cleanup_stuff list, indicating
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
        raise Exception("dummy")

    with pytest.raises(Exception):
        with app.app_context():
            client.get("/")

    assert len(cleanup_stuff) == 1
    assert isinstance(cleanup_stuff[0], Exception)
    assert str(cleanup_stuff[0]) == "dummy"


def test_app_ctx_globals_methods(app, app_ctx):
    """
    This function tests the context and global methods in a Flask application. It checks the functionality of the `g` object, which is a thread-local proxy to the request context. The function performs several operations on `flask.g` including getting values, checking for the presence of keys, setting default values, popping values, and iterating over keys. It also includes assertions to validate the expected behavior of these operations.
    
    Parameters:
    - app: The Flask application instance.
    - app_ctx: The application context for
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
    called = []

    @app.teardown_request
    def teardown_req(error=None):
        called.append("request")

    @app.teardown_appcontext
    def teardown_app(error=None):
        called.append("app")

    @app.route("/")
    def index():
        with flask._app_ctx_stack.top:
            with flask._request_ctx_stack.top:
                pass
        env = flask._request_ctx_stack.top.request.environ
        assert env["werkzeug.request"] is not None
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
t_app
