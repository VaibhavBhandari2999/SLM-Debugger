import pytest

try:
    import blinker
except ImportError:
    blinker = None

import flask

pytestmark = pytest.mark.skipif(
    blinker is None, reason="Signals require the blinker library."
)


def test_template_rendered(app, client):
    """
    Tests that a template is rendered correctly.
    
    This function checks if a specified template is rendered with the correct context. It connects a function to the `template_rendered` event of the Flask application to record the rendered template and its context. After making a GET request to the root route, it verifies that the template was rendered once, and that the context contains the expected value for the 'whiskey' variable.
    
    Parameters:
    app (flask.Flask): The Flask application to test.
    client
    """

    @app.route("/")
    def index():
        return flask.render_template("simple_template.html", whiskey=42)

    recorded = []

    def record(sender, template, context):
        recorded.append((template, context))

    flask.template_rendered.connect(record, app)
    try:
        client.get("/")
        assert len(recorded) == 1
        template, context = recorded[0]
        assert template.name == "simple_template.html"
        assert context["whiskey"] == 42
    finally:
        flask.template_rendered.disconnect(record, app)


def test_before_render_template():
    app = flask.Flask(__name__)

    @app.route("/")
    def index():
        return flask.render_template("simple_template.html", whiskey=42)

    recorded = []

    def record(sender, template, context):
        context["whiskey"] = 43
        recorded.append((template, context))

    flask.before_render_template.connect(record, app)
    try:
        rv = app.test_client().get("/")
        assert len(recorded) == 1
        template, context = recorded[0]
        assert template.name == "simple_template.html"
        assert context["whiskey"] == 43
        assert rv.data == b"<h1>43</h1>"
    finally:
        flask.before_render_template.disconnect(record, app)


def test_request_signals():
    """
    Tests the request signal handling in a Flask application.
    
    This function sets up a Flask application with specific before and after request handlers and signals. It connects custom signal handlers to the request_started and request_finished signals. It then makes a GET request to the '/' endpoint and asserts that the response data is as expected. The function also verifies the order and execution of the signal and handler calls.
    
    Key Parameters:
    - None
    
    Returns:
    - None
    
    Note:
    - The function uses the Flask testing client to make requests
    """

    app = flask.Flask(__name__)
    calls = []

    def before_request_signal(sender):
        calls.append("before-signal")

    def after_request_signal(sender, response):
        assert response.data == b"stuff"
        calls.append("after-signal")

    @app.before_request
    def before_request_handler():
        calls.append("before-handler")

    @app.after_request
    def after_request_handler(response):
        calls.append("after-handler")
        response.data = "stuff"
        return response

    @app.route("/")
    def index():
        calls.append("handler")
        return "ignored anyway"

    flask.request_started.connect(before_request_signal, app)
    flask.request_finished.connect(after_request_signal, app)

    try:
        rv = app.test_client().get("/")
        assert rv.data == b"stuff"

        assert calls == [
            "before-signal",
            "before-handler",
            "handler",
            "after-handler",
            "after-signal",
        ]
    finally:
        flask.request_started.disconnect(before_request_signal, app)
        flask.request_finished.disconnect(after_request_signal, app)


def test_request_exception_signal():
    app = flask.Flask(__name__)
    recorded = []

    @app.route("/")
    def index():
        1 // 0

    def record(sender, exception):
        recorded.append(exception)

    flask.got_request_exception.connect(record, app)
    try:
        assert app.test_client().get("/").status_code == 500
        assert len(recorded) == 1
        assert isinstance(recorded[0], ZeroDivisionError)
    finally:
        flask.got_request_exception.disconnect(record, app)


def test_appcontext_signals():
    """
    Tests the behavior of application context signals in a Flask application.
    
    This function sets up a Flask application with specific signals for application context push and pop. It then makes a test GET request to the root route of the application and verifies that the signals are triggered correctly.
    
    Key Parameters:
    - None
    
    Key Keywords:
    - None
    
    Inputs:
    - None
    
    Outputs:
    - None
    
    Expected Behavior:
    - The function should create an application context, trigger the `appcontext_pushed` signal, make a test GET
    """

    app = flask.Flask(__name__)
    recorded = []

    def record_push(sender, **kwargs):
        recorded.append("push")

    def record_pop(sender, **kwargs):
        recorded.append("pop")

    @app.route("/")
    def index():
        return "Hello"

    flask.appcontext_pushed.connect(record_push, app)
    flask.appcontext_popped.connect(record_pop, app)
    try:
        with app.test_client() as c:
            rv = c.get("/")
            assert rv.data == b"Hello"
            assert recorded == ["push"]
        assert recorded == ["push", "pop"]
    finally:
        flask.appcontext_pushed.disconnect(record_push, app)
        flask.appcontext_popped.disconnect(record_pop, app)


def test_flash_signal(app):
    @app.route("/")
    def index():
        flask.flash("This is a flash message", category="notice")
        return flask.redirect("/other")

    recorded = []

    def record(sender, message, category):
        recorded.append((message, category))

    flask.message_flashed.connect(record, app)
    try:
        client = app.test_client()
        with client.session_transaction():
            client.get("/")
            assert len(recorded) == 1
            message, category = recorded[0]
            assert message == "This is a flash message"
            assert category == "notice"
    finally:
        flask.message_flashed.disconnect(record, app)


def test_appcontext_tearing_down_signal():
    """
    Test the app context tearing down signal.
    
    This function sets up an application context, connects a signal handler for app context tearing down, and tests the behavior when a route raises an exception. It ensures that the signal handler is called with the appropriate arguments when the application context is properly torn down.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - Sets up a Flask application.
    - Connects a signal handler to the app context tearing down signal.
    - Tests the route handling of a division
    """

    app = flask.Flask(__name__)
    recorded = []

    def record_teardown(sender, **kwargs):
        recorded.append(("tear_down", kwargs))

    @app.route("/")
    def index():
        1 // 0

    flask.appcontext_tearing_down.connect(record_teardown, app)
    try:
        with app.test_client() as c:
            rv = c.get("/")
            assert rv.status_code == 500
            assert recorded == []
        assert recorded == [("tear_down", {"exc": None})]
    finally:
        flask.appcontext_tearing_down.disconnect(record_teardown, app)
