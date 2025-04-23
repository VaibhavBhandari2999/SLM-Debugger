from werkzeug.routing import BaseConverter

from flask import request
from flask import session
from flask import url_for


def test_custom_converters(app, client):
    """
    This function tests custom URL converters in a Flask application.
    
    Key Parameters:
    - app: The Flask application object.
    - client: The test client for the Flask application.
    
    The function defines a custom URL converter `ListConverter` that converts a comma-separated string to a list and vice versa. It then registers this converter with the Flask application and uses it in a route. The function also includes a test case to ensure that the custom converter works as expected.
    
    The function does not return any value but performs the
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
            
            This function asserts that the 'request' and 'session' objects are not None before processing the input value.
            
            Parameters:
            value (Any): The value to be converted to a Python object.
            
            Returns:
            Any: The converted Python object.
            
            Raises:
            AssertionError: If 'request' or 'session' is None.
            """

            assert request is not None
            assert session is not None
            return value

    app.url_map.converters["ctx"] = ContextConverter

    @app.get("/<ctx:name>")
    def index(name):
        return name

    assert client.get("/admin").data == b"admin"
