import pytest

import flask


def test_basic_url_generation(app):
    """
    Generate a URL for a specific endpoint.
    
    This function tests the generation of a basic URL for a given endpoint using the Flask framework. It sets the server name and preferred URL scheme in the application configuration and then generates the URL for the 'index' endpoint.
    
    Parameters:
    app (Flask): The Flask application object.
    
    Returns:
    str: The generated URL for the 'index' endpoint.
    
    Key Points:
    - The server name is set to "localhost".
    - The preferred URL scheme is set to
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
    with app.app_context():
        with pytest.raises(RuntimeError):
            flask.url_for("index")


def test_url_generation_without_context_fails():
    with pytest.raises(RuntimeError):
        flask.url_for("index")


def test_request_context_means_app_context(app):
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
    """
    Function to test application teardown with handled exception.
    
    This function sets up a teardown app context to capture exceptions and verifies that the exception is handled correctly.
    
    Parameters:
    app (Flask): The Flask application to test.
    
    Returns:
    None: The function asserts that the cleanup list contains a single None value, indicating that the exception was handled.
    """

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
    Tests the context refcounts for a Flask application.
    
    This function sets up a Flask application with custom teardown functions for both request and application contexts. It then makes a GET request to the root route of the application and checks that the teardown functions are called in the correct order. The function also ensures that the Werkzeug request environment is properly set up within the context.
    
    Parameters:
    app (Flask): The Flask application to test.
    client (TestClient): The test client for the Flask application.
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
    """
    This function tests the teardown mechanisms of a Flask application context. It sets up a Flask app with testing mode disabled and defines two teardown functions: one for request and one for application context. It then attempts to run a test request context, which should trigger these teardown functions. The function asserts that the teardown functions were called in the correct order and that the current application context is not present after the teardown.
    
    Key Parameters:
    - app: The Flask application object.
    
    Input:
    - None
    
    Output:
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
