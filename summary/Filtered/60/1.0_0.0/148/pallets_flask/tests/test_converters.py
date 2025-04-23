from werkzeug.routing import BaseConverter

from flask import request
from flask import session
from flask import url_for


def test_custom_converters(app, client):
    """
    This function tests custom URL converters in a Flask application. It defines a custom 'ListConverter' that converts comma-separated strings to a list and vice versa. The function sets up a Flask application with a route that uses this custom converter. It then performs a test GET request to the route with a comma-separated string and checks if the response matches the expected output. Additionally, it tests the URL generation using the `url_for` function.
    
    Parameters:
    - app: The Flask application object.
    - client:
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
    class ContextConverter(BaseConverter):
        def to_python(self, value):
            """
            Converts the given value to a Python object.
            
            Args:
            value: The value to be converted.
            
            Raises:
            AssertionError: If 'request' or 'session' is None.
            
            Returns:
            The converted Python object.
            """

            assert request is not None
            assert session is not None
            return value

    app.url_map.converters["ctx"] = ContextConverter

    @app.get("/<ctx:name>")
    def index(name):
        return name

    assert client.get("/admin").data == b"admin"
