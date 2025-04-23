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
    
    This function checks that attempting to generate a URL without providing a server name raises a RuntimeError.
    
    Parameters:
    app (Flask): The Flask application context to use for the test.
    
    Returns:
    None: This function raises a RuntimeError if the URL generation is attempted without a server name.
    
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
    """
    Tests the context of a request in a Flask application.
    
    This function checks whether the request context means an application context in a Flask application. It enters a test request context for the application and asserts that the current application object is the one passed to the function. After exiting the context, it asserts that the top of the application context stack is None.
    
    Parameters:
    app (Flask): The Flask application to test.
    
    Returns:
    None
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
    """
    Tests the application's teardown and error handling mechanism when an exception is raised during a request.
    
    This function sets up an application context with a custom teardown function that appends any exceptions to a list. It also sets up an error handler to return a JSON response for exceptions. The function then makes a GET request to the root URL and checks that the teardown function was called with a None value, indicating that the exception was handled by the application's error handler.
    
    Parameters:
    app (Flask): The
    """

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
    """
    This function configures a Flask application to use a custom application context global class. The custom class, CustomRequestGlobals, is initialized with a spam attribute set to 'eggs'. The function sets this class as the app_ctx_globals_class for the Flask app. When an application context is pushed, the custom class is used to provide global attributes accessible via the 'g' object within the context. The function then tests this setup by rendering a simple Jinja2 template string that outputs the value of '
    """

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
