import logging

import pytest
import werkzeug.serving
from jinja2 import TemplateNotFound
from markupsafe import Markup

import flask


def test_context_processing(app, client):
    """
    This function tests the context processing in a Flask application.
    
    Key Parameters:
    - app: The Flask application object.
    - client: The test client for the Flask application.
    
    The function sets up a context processor to inject a value into the template context and defines a route that renders a template with a value. It then sends a GET request to the route and asserts that the response data contains the expected values.
    
    Input:
    - Flask application instance.
    - Test client for the Flask application.
    
    Output:
    - None.
    """

    @app.context_processor
    def context_processor():
        return {"injected_value": 42}

    @app.route("/")
    def index():
        """
        Render a template with non-escaping text and HTML.
        
        This function renders a template named 'non_escaping_template.txt' and passes two variables to it:
        - 'text': A plain text string.
        - 'html': A Markup object containing the same text, which will be rendered as HTML.
        
        Parameters:
        None
        
        Returns:
        A rendered HTML template with the provided text and HTML content.
        
        Notes:
        The 'text' variable is used for plain text content, while the 'html' variable
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
    """
    Tests a simple stream response from a Flask application.
    
    This function sends a GET request to the root route of a Flask application and checks if the response data is equal to b'42'. The route returns a streamed template with a configuration value of 42.
    
    Parameters:
    app (flask.Flask): The Flask application to test.
    client: The test client for the Flask application.
    
    Returns:
    None: The function asserts the equality of the response data and b'42'.
    """

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
    """
    This function tests the usage of a template filter in a Flask application. It defines a filter `super_reverse` that reverses a string and applies it in a template. The function sets up a Flask application with a route that renders a template using this filter. The test checks if the filter is correctly applied to the string "abcd", expecting the output to be "dcba".
    
    Parameters:
    app (Flask): The Flask application object.
    client: A test client for the Flask application.
    """

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
    """
    This function tests the addition of a template test to an application. It checks if a value is a boolean and returns a success message if the test passes.
    
    Key Parameters:
    - app: The Flask application to which the template test will be added.
    - client: A test client for the Flask application used to make requests.
    
    Input:
    - A Flask application instance.
    - A test client for the Flask application.
    
    Output:
    - None. The function runs a test and asserts the expected outcome.
    
    Functionality:
    """

    def is_boolean(value):
        return isinstance(value, bool)

    app.add_template_test(is_boolean, "boolean")

    @app.route("/")
    def index():
        return flask.render_template("template_test.html", value=False)

    rv = client.get("/")
    assert b"Success!" in rv.data


def test_add_template_global(app, app_ctx):
    @app.template_global()
    def get_stuff():
        return 42

    assert "get_stuff" in app.jinja_env.globals.keys()
    assert app.jinja_env.globals["get_stuff"] == get_stuff
    assert app.jinja_env.globals["get_stuff"](), 42

    rv = flask.render_template_string("{{ get_stuff() }}")
    assert rv == "42"


def test_custom_template_loader(client):
    class MyFlask(flask.Flask):
        def create_global_jinja_loader(self):
            """
            Creates a Jinja2 template loader with a single template.
            
            This function initializes a Jinja2 `DictLoader` with a single template named 'index.html'. The template content is set to 'Hello Custom World!'.
            
            Parameters:
            None
            
            Returns:
            jinja2.DictLoader: A Jinja2 template loader object with the specified template.
            
            Usage:
            loader = create_global_jinja_loader()
            template = loader.get_template('index.html')
            rendered_content = template.render()
            """

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
    """
    Tests the template loader debugging functionality in a Flask application.
    
    This function sets up a test environment with a Flask application and a blueprint, configures the application to explain template loading, and checks if the template loader debug messages are generated correctly when a template is not found.
    
    Parameters:
    test_apps (fixture): A fixture providing the test application.
    monkeypatch (fixture): A fixture for monkeypatching behavior during tests.
    
    Returns:
    None: This function is designed to assert conditions and raise exceptions,
    """

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
t
