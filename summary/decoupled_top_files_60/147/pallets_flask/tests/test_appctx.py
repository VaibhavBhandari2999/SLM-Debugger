import pytest

import flask


def test_basic_url_generation(app):
    """
    Generate a URL for a given endpoint.
    
    This function tests the generation of a basic URL for a specified endpoint within a Flask application. It sets the server name and preferred URL scheme before generating the URL.
    
    Parameters:
    app (Flask): The Flask application context.
    
    Returns:
    str: The generated URL for the specified endpoint.
    
    Usage:
    >>> app = Flask(__name__)
    >>> app.config["SERVER_NAME"] = "localhost"
    >>> app.config["PREFERRED_URL_SCHEME"] =
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
    """
    Tests the request context to ensure it correctly sets and removes the application context.
    
    This function checks that entering a request context with the test client context manager sets the current application to the provided app and that exiting the context removes the application context from the top of the application context stack.
    
    Parameters:
    app (Flask): The Flask application to test the context with.
    
    Returns:
    None: This function does not return any value. It asserts conditions to test the application context.
    """

    with app.test_request_context():
        assert flask.current_app._get_current_object() == app
    assert flask._app_ctx_stack.top is None


def test_app_context_provides_current_app(app):
    with app.app_context():
        assert flask.current_app._get_current_object() == app
    assert flask._app_ctx_stack.top is None


def test_app_tearing_down(app):
    """
    Function to test application teardown functionality.
    
    This function sets up a teardown handler for the application context and ensures that it is called correctly.
    
    Parameters:
    app (Flask): The Flask application to which the teardown handler will be attached.
    
    Returns:
    None: The function does not return any value. It appends exceptions to a list during teardown.
    
    Key Points:
    - The function attaches a teardown handler to the application context.
    - The teardown handler appends any exceptions to a list named `cleanup_stuff`.
    """

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
    
    This function sets up a teardown app context for an application and tests how it handles exceptions. It appends any exceptions caught during teardown to a list and asserts that the list contains a single `None` value, indicating that the teardown handled the exception properly.
    
    Parameters:
    app (Flask): The Flask application to test.
    
    Returns:
    None: This function does not return any value. It asserts that the teardown process correctly handles exceptions.
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
    """
    This function tests various methods of the application context globals (flask.g) within a Flask application. It checks the functionality of getting values, checking for the presence of keys, setting default values, popping values, and iterating over the context. The function operates within the context of a Flask application and its application context.
    
    Parameters:
    - app: The Flask application instance.
    - app_ctx: The application context for the Flask application.
    
    Returns:
    - None: The function performs tests and assertions but does not return
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
    """
    This function tests the teardown mechanisms for a Flask application context. It sets up a testing environment and defines custom teardown functions for both request and application context. The function then enters a test request context and checks the sequence of events and the state of the application after the teardown process.
    
    Key Parameters:
    - app: The Flask application instance to be tested.
    
    Input:
    - None
    
    Output:
    - A list indicating the sequence of events and the state of the application after the teardown process.
    
    Returns:
    - A list
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
