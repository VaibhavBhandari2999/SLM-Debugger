import logging

import pytest
import werkzeug.serving
from jinja2 import TemplateNotFound
from markupsafe import Markup

import flask


def test_context_processing(app, client):
    """
    Tests the context processing functionality in a Flask application.
    
    This function sets up a Flask application with a context processor that injects a value into the template context. It also defines a route that renders a template with a specific value. The function then sends a GET request to the route and checks if the rendered template contains the expected values.
    
    Parameters:
    app (Flask): The Flask application to test.
    client (TestClient): The test client for the Flask application.
    
    Returns:
    None: The
    """

    @app.context_processor
    def context_processor():
        return {"injected_value": 42}

    @app.route("/")
    def index():
        """
        Render multiple templates using Flask's render_template function.
        
        This function renders a list of HTML templates and passes a context variable 'value' with the value 23 to each template.
        
        Parameters:
        None
        
        Returns:
        A rendered HTML response from the templates specified in the list.
        
        Note:
        - The first template in the list, 'no_template.xml', is skipped.
        - The remaining templates, 'simple_template.html' and 'context_template.html', are rendered and the 'value' context
        """

        return flask.render_template("context_template.html", value=23)

    rv = client.get("/")
    assert rv.data == b"<p>23|42"


def test_original_win(app, client):
    @app.route("/")
    def index():
        return flask.render_template_string("{{ config }}", config=42)

    rv = client.get("/")
    assert rv.data == b"42"


def test_simple_stream(app, client):
    @app.route("/")
    def index():
        return flask.stream_template_string("{{ config }}", config=42)

    rv = client.get("/")
    assert rv.data == b"42"


def test_request_less_rendering(app, app_ctx):
    app.config["WORLD_NAME"] = "Special World"

    @app.context_processor
    def context_processor():
        return dict(foo=42)

    rv = flask.render_template_string("Hello {{ config.WORLD_NAME }} {{ foo }}")
    assert rv == "Hello Special World 42"


def test_standard_context(app, client):
    """
    Tests the standard context in a Flask application. This function sets up a route that modifies the Flask global context and session, then renders a template with values from the request arguments, global context, configuration, and session. The function uses a test client to make a GET request to the route and asserts the response data matches the expected values.
    
    Parameters:
    - app (Flask): The Flask application to configure and test.
    - client (TestClient): The test client for the Flask application.
    
    Returns:
    -
    """

    @app.route("/")
    def index():
        flask.g.foo = 23
        flask.session["test"] = "aha"
        return flask.render_template_string(
            """
            {{ request.args.foo }}
            {{ g.foo }}
            {{ config.DEBUG }}
            {{ session.test }}
        """
        )

    rv = client.get("/?foo=42")
    assert rv.data.split() == [b"42", b"23", b"False", b"aha"]


def test_escaping(app, client):
    text = "<p>Hello World!"

    @app.route("/")
    def index():
        return flask.render_template(
            "escaping_template.html", text=text, html=Markup(text)
        )

    lines = client.get("/").data.splitlines()
    assert lines == [
        b"&lt;p&gt;Hello World!",
        b"<p>Hello World!",
        b"<p>Hello World!",
        b"<p>Hello World!",
        b"&lt;p&gt;Hello World!",
        b"<p>Hello World!",
    ]


def test_no_escaping(app, client):
    text = "<p>Hello World!"

    @app.route("/")
    def index():
        return flask.render_template(
            "non_escaping_template.txt", text=text, html=Markup(text)
        )

    lines = client.get("/").data.splitlines()
    assert lines == [
        b"<p>Hello World!",
        b"<p>Hello World!",
        b"<p>Hello World!",
        b"<p>Hello World!",
        b"&lt;p&gt;Hello World!",
        b"<p>Hello World!",
        b"<p>Hello World!",
        b"<p>Hello World!",
    ]


def test_escaping_without_template_filename(app, client, req_ctx):
    assert flask.render_template_string("{{ foo }}", foo="<test>") == "&lt;test&gt;"
    assert flask.render_template("mail.txt", foo="<test>") == "<test> Mail"


def test_macros(app, req_ctx):
    macro = flask.get_template_attribute("_macro.html", "hello")
    assert macro("World") == "Hello World!"


def test_template_filter(app):
    @app.template_filter()
    def my_reverse(s):
        return s[::-1]

    assert "my_reverse" in app.jinja_env.filters.keys()
    assert app.jinja_env.filters["my_reverse"] == my_reverse
    assert app.jinja_env.filters["my_reverse"]("abcd") == "dcba"


def test_add_template_filter(app):
    def my_reverse(s):
        return s[::-1]

    app.add_template_filter(my_reverse)
    assert "my_reverse" in app.jinja_env.filters.keys()
    assert app.jinja_env.filters["my_reverse"] == my_reverse
    assert app.jinja_env.filters["my_reverse"]("abcd") == "dcba"


def test_template_filter_with_name(app):
    @app.template_filter("strrev")
    def my_reverse(s):
        return s[::-1]

    assert "strrev" in app.jinja_env.filters.keys()
    assert app.jinja_env.filters["strrev"] == my_reverse
    assert app.jinja_env.filters["strrev"]("abcd") == "dcba"


def test_add_template_filter_with_name(app):
    def my_reverse(s):
        return s[::-1]

    app.add_template_filter(my_reverse, "strrev")
    assert "strrev" in app.jinja_env.filters.keys()
    assert app.jinja_env.filters["strrev"] == my_reverse
    assert app.jinja_env.filters["strrev"]("abcd") == "dcba"


def test_template_filter_with_template(app, client):
    @app.template_filter()
    def super_reverse(s):
        return s[::-1]

    @app.route("/")
    def index():
        return flask.render_template("template_filter.html", value="abcd")

    rv = client.get("/")
    assert rv.data == b"dcba"


def test_add_template_filter_with_template(app, client):
    def super_reverse(s):
        return s[::-1]

    app.add_template_filter(super_reverse)

    @app.route("/")
    def index():
        return flask.render_template("template_filter.html", value="abcd")

    rv = client.get("/")
    assert rv.data == b"dcba"


def test_template_filter_with_name_and_template(app, client):
    @app.template_filter("super_reverse")
    def my_reverse(s):
        return s[::-1]

    @app.route("/")
    def index():
        return flask.render_template("template_filter.html", value="abcd")

    rv = client.get("/")
    assert rv.data == b"dcba"


def test_add_template_filter_with_name_and_template(app, client):
    """
    This function tests adding a custom template filter with a specified name and template. It defines a function `my_reverse` that reverses a string. This function is then added as a template filter named 'super_reverse'. A route is created that renders a template, passing a string to be filtered. The test checks if the rendered output matches the expected reversed string.
    
    Parameters:
    - app: The Flask application object.
    - client: The test client for the Flask application.
    
    Returns:
    - None: This function
    """

    def my_reverse(s):
        return s[::-1]

    app.add_template_filter(my_reverse, "super_reverse")

    @app.route("/")
    def index():
        return flask.render_template("template_filter.html", value="abcd")

    rv = client.get("/")
    assert rv.data == b"dcba"


def test_template_test(app):
    @app.template_test()
    def boolean(value):
        return isinstance(value, bool)

    assert "boolean" in app.jinja_env.tests.keys()
    assert app.jinja_env.tests["boolean"] == boolean
    assert app.jinja_env.tests["boolean"](False)


def test_add_template_test(app):
    def boolean(value):
        return isinstance(value, bool)

    app.add_template_test(boolean)
    assert "boolean" in app.jinja_env.tests.keys()
    assert app.jinja_env.tests["boolean"] == boolean
    assert app.jinja_env.tests["boolean"](False)


def test_template_test_with_name(app):
    @app.template_test("boolean")
    def is_boolean(value):
        return isinstance(value, bool)

    assert "boolean" in app.jinja_env.tests.keys()
    assert app.jinja_env.tests["boolean"] == is_boolean
    assert app.jinja_env.tests["boolean"](False)


def test_add_template_test_with_name(app):
    """
    Add a custom Jinja2 template test to the application's environment.
    
    This function adds a custom Jinja2 template test to the application's Jinja2 environment. The test checks if a given value is a boolean.
    
    Parameters:
    app (object): The application object with a Jinja2 environment.
    is_boolean (function): A function that takes a value and returns True if the value is a boolean, otherwise False.
    
    Returns:
    None: The function modifies the Jinja2 environment of
    """

    def is_boolean(value):
        return isinstance(value, bool)

    app.add_template_test(is_boolean, "boolean")
    assert "boolean" in app.jinja_env.tests.keys()
    assert app.jinja_env.tests["boolean"] == is_boolean
    assert app.jinja_env.tests["boolean"](False)


def test_template_test_with_template(app, client):
    @app.template_test()
    def boolean(value):
        return isinstance(value, bool)

    @app.route("/")
    def index():
        return flask.render_template("template_test.html", value=False)

    rv = client.get("/")
    assert b"Success!" in rv.data


def test_add_template_test_with_template(app, client):
    def boolean(value):
        return isinstance(value, bool)

    app.add_template_test(boolean)

    @app.route("/")
    def index():
        return flask.render_template("template_test.html", value=False)

    rv = client.get("/")
    assert b"Success!" in rv.data


def test_template_test_with_name_and_template(app, client):
    @app.template_test("boolean")
    def is_boolean(value):
        return isinstance(value, bool)

    @app.route("/")
    def index():
        return flask.render_template("template_test.html", value=False)

    rv = client.get("/")
    assert b"Success!" in rv.data


def test_add_template_test_with_name_and_template(app, client):
    def is_boolean(value):
        return isinstance(value, bool)

    app.add_template_test(is_boolean, "boolean")

    @app.route("/")
    def index():
        return flask.render_template("template_test.html", value=False)

    rv = client.get("/")
    assert b"Success!" in rv.data


def test_add_template_global(app, app_ctx):
    """
    Tests the functionality of adding a template global to an application.
    
    This function checks that a template global function is correctly added to the Jinja environment and can be used in templates. It ensures that the function is available in the global namespace, that it can be called from within a Jinja template, and that it returns the expected value.
    
    Parameters:
    app (Flask): The Flask application object.
    app_ctx (Flask.appcontext): The application context for the Flask application.
    
    Returns:
    """

    @app.template_global()
    def get_stuff():
        return 42

    assert "get_stuff" in app.jinja_env.globals.keys()
    assert app.jinja_env.globals["get_stuff"] == get_stuff
    assert app.jinja_env.globals["get_stuff"](), 42

    rv = flask.render_template_string("{{ get_stuff() }}")
    assert rv == "42"


def test_custom_template_loader(client):
    """
    Tests a custom Jinja2 template loader in a Flask application.
    
    This function sets up a custom Jinja2 template loader that returns a predefined string "Hello Custom World!" when rendering the "index.html" template. It then makes a GET request to the root URL of the Flask application and asserts that the response data matches the expected output.
    
    Parameters:
    client (flask.testing.FlaskClient): The Flask test client used to make the request.
    
    Returns:
    None: The function asserts that the
    """

    class MyFlask(flask.Flask):
        def create_global_jinja_loader(self):
            from jinja2 import DictLoader

            return DictLoader({"index.html": "Hello Custom World!"})

    app = MyFlask(__name__)

    @app.route("/")
    def index():
        return flask.render_template("index.html")

    c = app.test_client()
    rv = c.get("/")
    assert rv.data == b"Hello Custom World!"


def test_iterable_loader(app, client):
    @app.context_processor
    def context_processor():
        return {"whiskey": "Jameson"}

    @app.route("/")
    def index():
        return flask.render_template(
            [
                "no_template.xml",  # should skip this one
                "simple_template.html",  # should render this
                "context_template.html",
            ],
            value=23,
        )

    rv = client.get("/")
    assert rv.data == b"<h1>Jameson</h1>"


def test_templates_auto_reload(app):
    # debug is False, config option is None
    assert app.debug is False
    assert app.config["TEMPLATES_AUTO_RELOAD"] is None
    assert app.jinja_env.auto_reload is False
    # debug is False, config option is False
    app = flask.Flask(__name__)
    app.config["TEMPLATES_AUTO_RELOAD"] = False
    assert app.debug is False
    assert app.jinja_env.auto_reload is False
    # debug is False, config option is True
    app = flask.Flask(__name__)
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    assert app.debug is False
    assert app.jinja_env.auto_reload is True
    # debug is True, config option is None
    app = flask.Flask(__name__)
    app.config["DEBUG"] = True
    assert app.config["TEMPLATES_AUTO_RELOAD"] is None
    assert app.jinja_env.auto_reload is True
    # debug is True, config option is False
    app = flask.Flask(__name__)
    app.config["DEBUG"] = True
    app.config["TEMPLATES_AUTO_RELOAD"] = False
    assert app.jinja_env.auto_reload is False
    # debug is True, config option is True
    app = flask.Flask(__name__)
    app.config["DEBUG"] = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    assert app.jinja_env.auto_reload is True


def test_templates_auto_reload_debug_run(app, monkeypatch):
    def run_simple_mock(*args, **kwargs):
        pass

    monkeypatch.setattr(werkzeug.serving, "run_simple", run_simple_mock)

    app.run()
    assert not app.jinja_env.auto_reload

    app.run(debug=True)
    assert app.jinja_env.auto_reload


def test_template_loader_debugging(test_apps, monkeypatch):
    from blueprintapp import app

    called = []

    class _TestHandler(logging.Handler):
        def handle(self, record):
            called.append(True)
            text = str(record.msg)
            assert "1: trying loader of application 'blueprintapp'" in text
            assert (
                "2: trying loader of blueprint 'admin' (blueprintapp.apps.admin)"
            ) in text
            assert (
                "trying loader of blueprint 'frontend' (blueprintapp.apps.frontend)"
            ) in text
            assert "Error: the template could not be found" in text
            assert (
                "looked up from an endpoint that belongs to the blueprint 'frontend'"
            ) in text
            assert "See https://flask.palletsprojects.com/blueprints/#templates" in text

    with app.test_client() as c:
        monkeypatch.setitem(app.config, "EXPLAIN_TEMPLATE_LOADING", True)
        monkeypatch.setattr(
            logging.getLogger("blueprintapp"), "handlers", [_TestHandler()]
        )

        with pytest.raises(TemplateNotFound) as excinfo:
            c.get("/missing")

        assert "missing_template.html" in str(excinfo.value)

    assert len(called) == 1


def test_custom_jinja_env():
    class CustomEnvironment(flask.templating.Environment):
        pass

    class CustomFlask(flask.Flask):
        jinja_environment = CustomEnvironment

    app = CustomFlask(__name__)
    assert isinstance(app.jinja_env, CustomEnvironment)
