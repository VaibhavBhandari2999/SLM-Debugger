from werkzeug.routing import BaseConverter

from flask import has_request_context
from flask import url_for


def test_custom_converters(app, client):
    """
    This function tests custom URL converters in a Flask application.
    
    Parameters:
    app (Flask): The Flask application object.
    client (TestClient): The test client for the Flask application.
    
    Key Components:
    - `ListConverter`: A custom URL converter that splits a string into a list and joins a list into a string.
    - `app.route("/<list:args>")`: A route that accepts a list of arguments.
    - `index(args)`: A view function that joins the
    """

    class ListConverter(BaseConverter):
        def to_python(self, value):
            return value.split(",")

        def to_url(self, value):
            base_to_url = super().to_url
            return ",".join(base_to_url(x) for x in value)

    app.url_map.converters["list"] = ListConverter

    @app.route("/<list:args>")
    def index(args):
        return "|".join(args)

    assert client.get("/1,2,3").data == b"1|2|3"

    with app.test_request_context():
        assert url_for("index", args=[4, 5, 6]) == "/4,5,6"


def test_context_available(app, client):
    """
    This function tests the availability of the request context in a Flask application. It sets up a custom URL converter that asserts the presence of the request context during conversion. The function creates a Flask application with a route that uses this custom converter. It then makes a GET request to a specific URL and checks if the request context is available.
    
    Parameters:
    - app (Flask): The Flask application to configure and test.
    - client (TestClient): The test client to make requests to the application.
    
    Returns:
    """

    class ContextConverter(BaseConverter):
        def to_python(self, value):
            assert has_request_context()
            return value

    app.url_map.converters["ctx"] = ContextConverter

    @app.route("/<ctx:name>")
    def index(name):
        return name

    assert client.get("/admin").data == b"admin"
