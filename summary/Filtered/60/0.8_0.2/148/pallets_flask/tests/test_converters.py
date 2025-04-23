from werkzeug.routing import BaseConverter

from flask import request
from flask import session
from flask import url_for


def test_custom_converters(app, client):
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
    Tests the availability of the request and session objects within a custom context converter.
    
    This function sets up a Flask application with a custom URL converter that checks for the availability of the `request` and `session` objects. It then makes a GET request to a specific route to verify that these objects are correctly available in the context.
    
    Parameters:
    - app (Flask): The Flask application to configure and test.
    - client (FlaskClient): The test client for making requests to the Flask application.
    
    Returns
    """

    class ContextConverter(BaseConverter):
        def to_python(self, value):
            assert request is not None
            assert session is not None
            return value

    app.url_map.converters["ctx"] = ContextConverter

    @app.get("/<ctx:name>")
    def index(name):
        return name

    assert client.get("/admin").data == b"admin"
