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
    """
    Tests the request exception signal in a Flask application.
    
    This function sets up a simple Flask application with a route that intentionally raises a ZeroDivisionError. It then connects a custom exception handler to the 'got_request_exception' signal. After making a GET request to the route, it checks that the response status code is 500 (internal server error) and that the exception handler has recorded the error.
    
    Parameters:
    None
    
    Returns:
    None
    """

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


def test_appcontext_signals(app, client):
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
        rv = client.get("/")
        assert rv.data == b"Hello"
        assert recorded == ["push", "pop"]
    finally:
        flask.appcontext_pushed.disconnect(record_push, app)
        flask.appcontext_popped.disconnect(record_pop, app)


def test_flash_signal(app):
    """
    Tests the flash signal in a Flask application.
    
    This function sets up a route that flashes a message and then redirects to another route. It connects a callback to the message_flashed signal to record the flashed message and its category. The function then makes a GET request to the route and checks if the flashed message and category are recorded correctly.
    
    Parameters:
    app (Flask): The Flask application to test.
    
    Returns:
    None
    """

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


def test_appcontext_tearing_down_signal(app, client):
    """
    Test the app context tearing down signal.
    
    This function tests the app context tearing down signal by setting up an application with a route that raises a ZeroDivisionError. It connects a signal handler to record exceptions during app context teardown. The test sends a GET request to the route and verifies that the exception is recorded and the response status code is 500. Finally, it disconnects the signal handler.
    
    Parameters:
    app (flask.Flask): The Flask application to test.
    client (
    """

    app.testing = False
    recorded = []

    def record_teardown(sender, exc):
        recorded.append(exc)

    @app.route("/")
    def index():
        1 // 0

    flask.appcontext_tearing_down.connect(record_teardown, app)
    try:
        rv = client.get("/")
        assert rv.status_code == 500
        assert len(recorded) == 1
        assert isinstance(recorded[0], ZeroDivisionError)
    finally:
        flask.appcontext_tearing_down.disconnect(record_teardown, app)
