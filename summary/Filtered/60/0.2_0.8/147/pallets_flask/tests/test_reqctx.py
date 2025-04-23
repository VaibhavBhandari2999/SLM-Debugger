import pytest

import flask
from flask.sessions import SecureCookieSessionInterface
from flask.sessions import SessionInterface

try:
    from greenlet import greenlet
except ImportError:
    greenlet = None


def test_teardown_on_pop(app):
    buffer = []

    @app.teardown_request
    def end_of_request(exception):
        buffer.append(exception)

    ctx = app.test_request_context()
    ctx.push()
    assert buffer == []
    ctx.pop()
    assert buffer == [None]


def test_teardown_with_previous_exception(app):
    """
    Function to test the teardown request functionality in a Flask application.
    
    This function sets up a teardown request handler that appends any exceptions to a buffer. It then raises an exception and checks the buffer to ensure that the teardown handler correctly handles the absence of an exception.
    
    Parameters:
    app (Flask): The Flask application to test.
    
    Returns:
    None: This function does not return any value. It asserts the correct behavior of the teardown request handler.
    """

    buffer = []

    @app.teardown_request
    def end_of_request(exception):
        buffer.append(exception)

    try:
        raise Exception("dummy")
    except Exception:
        pass

    with app.test_request_context():
        assert buffer == []
    assert buffer == [None]


def test_teardown_with_handled_exception(app):
    buffer = []

    @app.teardown_request
    def end_of_request(exception):
        buffer.append(exception)

    with app.test_request_context():
        assert buffer == []
        try:
            raise Exception("dummy")
        except Exception:
            pass
    assert buffer == [None]


def test_proper_test_request_context(app):
    app.config.update(SERVER_NAME="localhost.localdomain:5000")

    @app.route("/")
    def index():
        return None

    @app.route("/", subdomain="foo")
    def sub():
        return None

    with app.test_request_context("/"):
        assert (
            flask.url_for("index", _external=True)
            == "http://localhost.localdomain:5000/"
        )

    with app.test_request_context("/"):
        assert (
            flask.url_for("sub", _external=True)
            == "http://foo.localhost.localdomain:5000/"
        )

    # suppress Werkzeug 0.15 warning about name mismatch
    with pytest.warns(None):
        with app.test_request_context(
            "/", environ_overrides={"HTTP_HOST": "localhost"}
        ):
            pass

    app.config.update(SERVER_NAME="localhost")
    with app.test_request_context("/", environ_overrides={"SERVER_NAME": "localhost"}):
        pass

    app.config.update(SERVER_NAME="localhost:80")
    with app.test_request_context(
        "/", environ_overrides={"SERVER_NAME": "localhost:80"}
    ):
        pass


def test_context_binding(app):
    @app.route("/")
    def index():
        return f"Hello {flask.request.args['name']}!"

    @app.route("/meh")
    def meh():
        return flask.request.url

    with app.test_request_context("/?name=World"):
        assert index() == "Hello World!"
    with app.test_request_context("/meh"):
        assert meh() == "http://localhost/meh"
    assert flask._request_ctx_stack.top is None


def test_context_test(app):
    assert not flask.request
    assert not flask.has_request_context()
    ctx = app.test_request_context()
    ctx.push()
    try:
        assert flask.request
        assert flask.has_request_context()
    finally:
        ctx.pop()


def test_manual_context_binding(app):
    """
    Test manual context binding for a Flask application.
    
    This function sets up a test request context with a specific URL and query parameter, then pushes the context to the stack. It verifies that the `index` view function returns the expected greeting. After the test, the context is popped to clean up, and an attempt to call `index` again raises a `RuntimeError` indicating that the context is no longer active.
    
    Parameters:
    app (flask.Flask): The Flask application to test.
    
    Returns
    """

    @app.route("/")
    def index():
        return f"Hello {flask.request.args['name']}!"

    ctx = app.test_request_context("/?name=World")
    ctx.push()
    assert index() == "Hello World!"
    ctx.pop()
    with pytest.raises(RuntimeError):
        index()


@pytest.mark.skipif(greenlet is None, reason="greenlet not installed")
class TestGreenletContextCopying:
    def test_greenlet_context_copying(self, app, client):
        greenlets = []

        @app.route("/")
        def index():
            """
            This function initializes a Flask session with a key-value pair, creates a request context, and starts a greenlet to execute a nested function. The nested function asserts the availability of the Flask request and current application objects within the context, and checks the request path, arguments, and session data. The function returns a string 'Hello World!' and appends the greenlet to a list.
            
            Parameters:
            None
            
            Returns:
            str: 'Hello World!'
            
            Note:
            - A greenlet is used to run
            """

            flask.session["fizz"] = "buzz"
            reqctx = flask._request_ctx_stack.top.copy()

            def g():
                assert not flask.request
                assert not flask.current_app
                with reqctx:
                    assert flask.request
                    assert flask.current_app == app
                    assert flask.request.path == "/"
                    assert flask.request.args["foo"] == "bar"
                    assert flask.session.get("fizz") == "buzz"
                assert not flask.request
                return 42

            greenlets.append(greenlet(g))
            return "Hello World!"

        rv = client.get("/?foo=bar")
        assert rv.data == b"Hello World!"

        result = greenlets[0].run()
        assert result == 42

    def test_greenlet_context_copying_api(self, app, client):
        greenlets = []

        @app.route("/")
        def index():
            flask.session["fizz"] = "buzz"

            @flask.copy_current_request_context
            def g():
                assert flask.request
                assert flask.current_app == app
                assert flask.request.path == "/"
                assert flask.request.args["foo"] == "bar"
                assert flask.session.get("fizz") == "buzz"
                return 42

            greenlets.append(greenlet(g))
            return "Hello World!"

        rv = client.get("/?foo=bar")
        assert rv.data == b"Hello World!"

        result = greenlets[0].run()
        assert result == 42


def test_session_error_pops_context():
    class SessionError(Exception):
        pass

    class FailingSessionInterface(SessionInterface):
        def open_session(self, app, request):
            raise SessionError()

    class CustomFlask(flask.Flask):
        session_interface = FailingSessionInterface()

    app = CustomFlask(__name__)

    @app.route("/")
    def index():
        # shouldn't get here
        AssertionError()

    response = app.test_client().get("/")
    assert response.status_code == 500
    assert not flask.request
    assert not flask.current_app


def test_session_dynamic_cookie_name():

    # This session interface will use a cookie with a different name if the
    # requested url ends with the string "dynamic_cookie"
    class PathAwareSessionInterface(SecureCookieSessionInterface):
        def get_cookie_name(self, app):
            if flask.request.url.endswith("dynamic_cookie"):
                return "dynamic_cookie_name"
            else:
                return super().get_cookie_name(app)

    class CustomFlask(flask.Flask):
        session_interface = PathAwareSessionInterface()

    app = CustomFlask(__name__)
    app.secret_key = "secret_key"

    @app.route("/set", methods=["POST"])
    def set():
        flask.session["value"] = flask.request.form["value"]
        return "value set"

    @app.route("/get")
    def get():
        v = flask.session.get("value", "None")
        return v

    @app.route("/set_dynamic_cookie", methods=["POST"])
    def set_dynamic_cookie():
        flask.session["value"] = flask.request.form["value"]
        return "value set"

    @app.route("/get_dynamic_cookie")
    def get_dynamic_cookie():
        v = flask.session.get("value", "None")
        return v

    test_client = app.test_client()

    # first set the cookie in both /set urls but each with a different value
    assert test_client.post("/set", data={"value": "42"}).data == b"value set"
    assert (
        test_client.post("/set_dynamic_cookie", data={"value": "616"}).data
        == b"value set"
    )

    # now check that the relevant values come back - meaning that different
    # cookies are being used for the urls that end with "dynamic cookie"
    assert test_client.get("/get").data == b"42"
    assert test_client.get("/get_dynamic_cookie").data == b"616"


def test_bad_environ_raises_bad_request():
    app = flask.Flask(__name__)

    from flask.testing import EnvironBuilder

    builder = EnvironBuilder(app)
    environ = builder.get_environ()

    # use a non-printable character in the Host - this is key to this test
    environ["HTTP_HOST"] = "\x8a"

    with app.request_context(environ):
        response = app.full_dispatch_request()
    assert response.status_code == 400


def test_environ_for_valid_idna_completes():
    app = flask.Flask(__name__)

    @app.route("/")
    def index():
        return "Hello World!"

    from flask.testing import EnvironBuilder

    builder = EnvironBuilder(app)
    environ = builder.get_environ()

    # these characters are all IDNA-compatible
    environ["HTTP_HOST"] = "ąśźäüжŠßя.com"

    with app.request_context(environ):
        response = app.full_dispatch_request()

    assert response.status_code == 200


def test_normal_environ_completes():
    """
    Tests the Flask application's response to a GET request at the root URL with a specific host header. The function sets up a Flask application with a single route that returns "Hello World!". It then sends a GET request to the root URL with the host header set to a non-ASCII domain name and asserts that the response status code is 200, indicating a successful request.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - Sets up a Flask application with a single
    """

    app = flask.Flask(__name__)

    @app.route("/")
    def index():
        return "Hello World!"

    response = app.test_client().get("/", headers={"host": "xn--on-0ia.com"})
    assert response.status_code == 200
