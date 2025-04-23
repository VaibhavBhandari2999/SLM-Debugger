import click
import pytest
import werkzeug

import flask
from flask import appcontext_popped
from flask.cli import ScriptInfo
from flask.globals import _cv_request
from flask.json import jsonify
from flask.testing import EnvironBuilder
from flask.testing import FlaskCliRunner


def test_environ_defaults_from_config(app, client):
    """
    Test the default behavior of the Flask application's environment settings.
    
    This function sets the `SERVER_NAME` and `APPLICATION_ROOT` configuration options in the Flask application's config. It then defines a simple route that returns the request URL. The function uses a test request context and a test client to verify that the URL is constructed correctly based on the configuration settings.
    
    Parameters:
    - app (flask.Flask): The Flask application instance.
    - client (flask.testing.FlaskClient): A test client for
    """

    app.config["SERVER_NAME"] = "example.com:1234"
    app.config["APPLICATION_ROOT"] = "/foo"

    @app.route("/")
    def index():
        return flask.request.url

    ctx = app.test_request_context()
    assert ctx.request.url == "http://example.com:1234/foo/"

    rv = client.get("/")
    assert rv.data == b"http://example.com:1234/foo/"


def test_environ_defaults(app, client, app_ctx, req_ctx):
    @app.route("/")
    def index():
        return flask.request.url

    ctx = app.test_request_context()
    assert ctx.request.url == "http://localhost/"
    with client:
        rv = client.get("/")
        assert rv.data == b"http://localhost/"


def test_environ_base_default(app, client, app_ctx):
    """
    This function tests the base default behavior of the Flask application environment setup.
    
    Parameters:
    app (Flask): The Flask application instance.
    client (TestClient): A test client for making requests to the Flask application.
    app_ctx (Flask.app_context): The application context for the Flask application.
    
    Returns:
    None: This function does not return any value. It performs a GET request to the root route of the Flask application and checks the response data and the user agent stored in the global
    """

    @app.route("/")
    def index():
        flask.g.user_agent = flask.request.headers["User-Agent"]
        return flask.request.remote_addr

    rv = client.get("/")
    assert rv.data == b"127.0.0.1"
    assert flask.g.user_agent == f"werkzeug/{werkzeug.__version__}"


def test_environ_base_modified(app, client, app_ctx):
    @app.route("/")
    def index():
        flask.g.user_agent = flask.request.headers["User-Agent"]
        return flask.request.remote_addr

    client.environ_base["REMOTE_ADDR"] = "0.0.0.0"
    client.environ_base["HTTP_USER_AGENT"] = "Foo"
    rv = client.get("/")
    assert rv.data == b"0.0.0.0"
    assert flask.g.user_agent == "Foo"

    client.environ_base["REMOTE_ADDR"] = "0.0.0.1"
    client.environ_base["HTTP_USER_AGENT"] = "Bar"
    rv = client.get("/")
    assert rv.data == b"0.0.0.1"
    assert flask.g.user_agent == "Bar"


def test_client_open_environ(app, client, request):
    @app.route("/index")
    def index():
        return flask.request.remote_addr

    builder = EnvironBuilder(app, path="/index", method="GET")
    request.addfinalizer(builder.close)

    rv = client.open(builder)
    assert rv.data == b"127.0.0.1"

    environ = builder.get_environ()
    client.environ_base["REMOTE_ADDR"] = "127.0.0.2"
    rv = client.open(environ)
    assert rv.data == b"127.0.0.2"


def test_specify_url_scheme(app, client):
    @app.route("/")
    def index():
        return flask.request.url

    ctx = app.test_request_context(url_scheme="https")
    assert ctx.request.url == "https://localhost/"

    rv = client.get("/", url_scheme="https")
    assert rv.data == b"https://localhost/"


def test_path_is_url(app):
    """
    Tests if the provided path is a URL.
    
    This function checks if the given path is a URL and extracts its components such as the scheme, host, script root, and path.
    
    Parameters:
    app (object): The application object used to build the environment.
    
    Returns:
    None: This function does not return any value. It asserts the correctness of the URL components.
    
    Example:
    >>> test_path_is_url(app)
    AssertionError: If the URL components are not as expected.
    """

    eb = EnvironBuilder(app, "https://example.com/")
    assert eb.url_scheme == "https"
    assert eb.host == "example.com"
    assert eb.script_root == ""
    assert eb.path == "/"


def test_environbuilder_json_dumps(app):
    """EnvironBuilder.json_dumps() takes settings from the app."""
    app.json.ensure_ascii = False
    eb = EnvironBuilder(app, json="\u20ac")
    assert eb.input_stream.read().decode("utf8") == '"\u20ac"'


def test_blueprint_with_subdomain():
    app = flask.Flask(__name__, subdomain_matching=True)
    app.config["SERVER_NAME"] = "example.com:1234"
    app.config["APPLICATION_ROOT"] = "/foo"
    client = app.test_client()

    bp = flask.Blueprint("company", __name__, subdomain="xxx")

    @bp.route("/")
    def index():
        return flask.request.url

    app.register_blueprint(bp)

    ctx = app.test_request_context("/", subdomain="xxx")
    assert ctx.request.url == "http://xxx.example.com:1234/foo/"

    with ctx:
        assert ctx.request.blueprint == bp.name

    rv = client.get("/", subdomain="xxx")
    assert rv.data == b"http://xxx.example.com:1234/foo/"


def test_redirect_keep_session(app, client, app_ctx):
    @app.route("/", methods=["GET", "POST"])
    def index():
        if flask.request.method == "POST":
            return flask.redirect("/getsession")
        flask.session["data"] = "foo"
        return "index"

    @app.route("/getsession")
    def get_session():
        return flask.session.get("data", "<missing>")

    with client:
        rv = client.get("/getsession")
        assert rv.data == b"<missing>"

        rv = client.get("/")
        assert rv.data == b"index"
        assert flask.session.get("data") == "foo"

        rv = client.post("/", data={}, follow_redirects=True)
        assert rv.data == b"foo"
        assert flask.session.get("data") == "foo"

        rv = client.get("/getsession")
        assert rv.data == b"foo"


def test_session_transactions(app, client):
    @app.route("/")
    def index():
        return str(flask.session["foo"])

    with client:
        with client.session_transaction() as sess:
            assert len(sess) == 0
            sess["foo"] = [42]
            assert len(sess) == 1
        rv = client.get("/")
        assert rv.data == b"[42]"
        with client.session_transaction() as sess:
            assert len(sess) == 1
            assert sess["foo"] == [42]


def test_session_transactions_no_null_sessions():
    app = flask.Flask(__name__)

    with app.test_client() as c:
        with pytest.raises(RuntimeError) as e:
            with c.session_transaction():
                pass
        assert "Session backend did not open a session" in str(e.value)


def test_session_transactions_keep_context(app, client, req_ctx):
    client.get("/")
    req = flask.request._get_current_object()
    assert req is not None
    with client.session_transaction():
        assert req is flask.request._get_current_object()


def test_session_transaction_needs_cookies(app):
    c = app.test_client(use_cookies=False)

    with pytest.raises(TypeError, match="Cookies are disabled."):
        with c.session_transaction():
            pass


def test_test_client_context_binding(app, client):
    app.testing = False

    @app.route("/")
    def index():
        flask.g.value = 42
        return "Hello World!"

    @app.route("/other")
    def other():
        1 // 0

    with client:
        resp = client.get("/")
        assert flask.g.value == 42
        assert resp.data == b"Hello World!"
        assert resp.status_code == 200

        resp = client.get("/other")
        assert not hasattr(flask.g, "value")
        assert b"Internal Server Error" in resp.data
        assert resp.status_code == 500
        flask.g.value = 23

    try:
        flask.g.value
    except (AttributeError, RuntimeError):
        pass
    else:
        raise AssertionError("some kind of exception expected")


def test_reuse_client(client):
    """
    Test the reusability of a client object.
    
    This function tests whether a client object can be reused multiple times without issues. The client is used within two separate 'with' blocks to make requests to the root endpoint and check the response status code.
    
    Parameters:
    client (TestClient): The client object to be tested for reusability.
    
    Returns:
    None: This function does not return any value. It performs assertions to validate the client's behavior.
    """

    c = client

    with c:
        assert client.get("/").status_code == 404

    with c:
        assert client.get("/").status_code == 404


def test_full_url_request(app, client):
    """
    Test a full URL request to a Flask application.
    
    This function sends a POST request to a specific route of a Flask application, including both form data and query parameters in the URL. It verifies that the request is processed correctly by checking the response status code and the contents of the request form and arguments.
    
    Parameters:
    app (Flask): The Flask application to test.
    client (TestClient): The test client for the Flask application.
    
    Returns:
    None: This function does not return anything.
    """

    @app.route("/action", methods=["POST"])
    def action():
        return "x"

    with client:
        rv = client.post("http://domain.com/action?vodka=42", data={"gin": 43})
        assert rv.status_code == 200
        assert "gin" in flask.request.form
        assert "vodka" in flask.request.args


def test_json_request_and_response(app, client):
    @app.route("/echo", methods=["POST"])
    def echo():
        return jsonify(flask.request.get_json())

    with client:
        json_data = {"drink": {"gin": 1, "tonic": True}, "price": 10}
        rv = client.post("/echo", json=json_data)

        # Request should be in JSON
        assert flask.request.is_json
        assert flask.request.get_json() == json_data

        # Response should be in JSON
        assert rv.status_code == 200
        assert rv.is_json
        assert rv.get_json() == json_data


def test_client_json_no_app_context(app, client):
    @app.route("/hello", methods=["POST"])
    def hello():
        return f"Hello, {flask.request.json['name']}!"

    class Namespace:
        count = 0

        def add(self, app):
            self.count += 1

    ns = Namespace()

    with appcontext_popped.connected_to(ns.add, app):
        rv = client.post("/hello", json={"name": "Flask"})

    assert rv.get_data(as_text=True) == "Hello, Flask!"
    assert ns.count == 1


def test_subdomain():
    app = flask.Flask(__name__, subdomain_matching=True)
    app.config["SERVER_NAME"] = "example.com"
    client = app.test_client()

    @app.route("/", subdomain="<company_id>")
    def view(company_id):
        return company_id

    with app.test_request_context():
        url = flask.url_for("view", company_id="xxx")

    with client:
        response = client.get(url)

    assert 200 == response.status_code
    assert b"xxx" == response.data


def test_nosubdomain(app, client):
    app.config["SERVER_NAME"] = "example.com"

    @app.route("/<company_id>")
    def view(company_id):
        return company_id

    with app.test_request_context():
        url = flask.url_for("view", company_id="xxx")

    with client:
        response = client.get(url)

    assert 200 == response.status_code
    assert b"xxx" == response.data


def test_cli_runner_class(app):
    runner = app.test_cli_runner()
    assert isinstance(runner, FlaskCliRunner)

    class SubRunner(FlaskCliRunner):
        pass

    app.test_cli_runner_class = SubRunner
    runner = app.test_cli_runner()
    assert isinstance(runner, SubRunner)


def test_cli_invoke(app):
    @app.cli.command("hello")
    def hello_command():
        click.echo("Hello, World!")

    runner = app.test_cli_runner()
    # invoke with command name
    result = runner.invoke(args=["hello"])
    assert "Hello" in result.output
    # invoke with command object
    result = runner.invoke(hello_command)
    assert "Hello" in result.output


def test_cli_custom_obj(app):
    class NS:
        called = False

    def create_app():
        NS.called = True
        return app

    @app.cli.command("hello")
    def hello_command():
        click.echo("Hello, World!")

    script_info = ScriptInfo(create_app=create_app)
    runner = app.test_cli_runner()
    runner.invoke(hello_command, obj=script_info)
    assert NS.called


def test_client_pop_all_preserved(app, req_ctx, client):
    """
    Tests the behavior of the Flask client when popping all contexts are preserved.
    
    This function checks that the request context and the client context are properly preserved after a request that uses `stream_with_context`.
    
    Parameters:
    - app: The Flask application to test.
    - req_ctx: The request context fixture.
    - client: The test client for the Flask application.
    
    The function performs the following steps:
    1. Defines a route that returns a streamed response using `stream_with_context`.
    2. Uses the `client` fixture
    """

    @app.route("/")
    def index():
        # stream_with_context pushes a third context, preserved by response
        return flask.stream_with_context("hello")

    # req_ctx fixture pushed an initial context
    with client:
        # request pushes a second request context, preserved by client
        rv = client.get("/")

    # close the response, releasing the context held by stream_with_context
    rv.close()
    # only req_ctx fixture should still be pushed
    assert _cv_request.get(None) is req_ctx
