import pytest
from werkzeug.http import parse_set_header

import flask.views


def common_test(app):
    """
    Tests the behavior of a Flask application's routes and methods.
    
    This function sends various HTTP requests to the root URL of a Flask application and checks the responses.
    
    Parameters:
    app (flask.Flask): The Flask application to test.
    
    Returns:
    None: This function performs assertions and does not return any value.
    """

    c = app.test_client()

    assert c.get("/").data == b"GET"
    assert c.post("/").data == b"POST"
    assert c.put("/").status_code == 405
    meths = parse_set_header(c.open("/", method="OPTIONS").headers["Allow"])
    assert sorted(meths) == ["GET", "HEAD", "OPTIONS", "POST"]


def test_basic_view(app):
    class Index(flask.views.View):
        methods = ["GET", "POST"]

        def dispatch_request(self):
            return flask.request.method

    app.add_url_rule("/", view_func=Index.as_view("index"))
    common_test(app)


def test_method_based_view(app):
    class Index(flask.views.MethodView):
        def get(self):
            return "GET"

        def post(self):
            return "POST"

    app.add_url_rule("/", view_func=Index.as_view("index"))

    common_test(app)


def test_view_patching(app):
    class Index(flask.views.MethodView):
        def get(self):
            1 // 0

        def post(self):
            1 // 0

    class Other(Index):
        def get(self):
            return "GET"

        def post(self):
            return "POST"

    view = Index.as_view("index")
    view.view_class = Other
    app.add_url_rule("/", view_func=view)
    common_test(app)


def test_view_inheritance(app, client):
    class Index(flask.views.MethodView):
        def get(self):
            return "GET"

        def post(self):
            return "POST"

    class BetterIndex(Index):
        def delete(self):
            return "DELETE"

    app.add_url_rule("/", view_func=BetterIndex.as_view("index"))

    meths = parse_set_header(client.open("/", method="OPTIONS").headers["Allow"])
    assert sorted(meths) == ["DELETE", "GET", "HEAD", "OPTIONS", "POST"]


def test_view_decorators(app, client):
    def add_x_parachute(f):
        """
        Decorator function to add an X-Parachute header to the response of a Flask route.
        
        This function is a decorator that wraps a Flask route function and adds an X-Parachute header to the response with the value "awesome".
        
        Parameters:
        f (function): The Flask route function to be decorated.
        
        Returns:
        function: A new function that wraps the original function and adds the X-Parachute header to the response.
        
        Usage:
        @app.route('/some_route')
        """

        def new_function(*args, **kwargs):
            resp = flask.make_response(f(*args, **kwargs))
            resp.headers["X-Parachute"] = "awesome"
            return resp

        return new_function

    class Index(flask.views.View):
        decorators = [add_x_parachute]

        def dispatch_request(self):
            return "Awesome"

    app.add_url_rule("/", view_func=Index.as_view("index"))
    rv = client.get("/")
    assert rv.headers["X-Parachute"] == "awesome"
    assert rv.data == b"Awesome"


def test_view_provide_automatic_options_attr():
    app = flask.Flask(__name__)

    class Index1(flask.views.View):
        provide_automatic_options = False

        def dispatch_request(self):
            return "Hello World!"

    app.add_url_rule("/", view_func=Index1.as_view("index"))
    c = app.test_client()
    rv = c.open("/", method="OPTIONS")
    assert rv.status_code == 405

    app = flask.Flask(__name__)

    class Index2(flask.views.View):
        methods = ["OPTIONS"]
        provide_automatic_options = True

        def dispatch_request(self):
            return "Hello World!"

    app.add_url_rule("/", view_func=Index2.as_view("index"))
    c = app.test_client()
    rv = c.open("/", method="OPTIONS")
    assert sorted(rv.allow) == ["OPTIONS"]

    app = flask.Flask(__name__)

    class Index3(flask.views.View):
        def dispatch_request(self):
            return "Hello World!"

    app.add_url_rule("/", view_func=Index3.as_view("index"))
    c = app.test_client()
    rv = c.open("/", method="OPTIONS")
    assert "OPTIONS" in rv.allow


def test_implicit_head(app, client):
    class Index(flask.views.MethodView):
        def get(self):
            return flask.Response("Blub", headers={"X-Method": flask.request.method})

    app.add_url_rule("/", view_func=Index.as_view("index"))
    rv = client.get("/")
    assert rv.data == b"Blub"
    assert rv.headers["X-Method"] == "GET"
    rv = client.head("/")
    assert rv.data == b""
    assert rv.headers["X-Method"] == "HEAD"


def test_explicit_head(app, client):
    class Index(flask.views.MethodView):
        def get(self):
            return "GET"

        def head(self):
            return flask.Response("", headers={"X-Method": "HEAD"})

    app.add_url_rule("/", view_func=Index.as_view("index"))
    rv = client.get("/")
    assert rv.data == b"GET"
    rv = client.head("/")
    assert rv.data == b""
    assert rv.headers["X-Method"] == "HEAD"


def test_endpoint_override(app):
    """
    Function to test endpoint override in a Flask application.
    
    This function configures a Flask application to include an endpoint and then attempts to add the same endpoint again, which should raise an AssertionError. However, the function also ensures that other tests still pass by logging a warning instead of failing.
    
    Parameters:
    app (flask.Flask): The Flask application to configure and test.
    
    Returns:
    None: This function does not return any value. It logs warnings and assertions.
    """

    app.debug = True

    class Index(flask.views.View):
        methods = ["GET", "POST"]

        def dispatch_request(self):
            return flask.request.method

    app.add_url_rule("/", view_func=Index.as_view("index"))

    with pytest.raises(AssertionError):
        app.add_url_rule("/", view_func=Index.as_view("index"))

    # But these tests should still pass. We just log a warning.
    common_test(app)


def test_methods_var_inheritance(app, client):
    class BaseView(flask.views.MethodView):
        methods = ["GET", "PROPFIND"]

    class ChildView(BaseView):
        def get(self):
            return "GET"

        def propfind(self):
            return "PROPFIND"

    app.add_url_rule("/", view_func=ChildView.as_view("index"))

    assert client.get("/").data == b"GET"
    assert client.open("/", method="PROPFIND").data == b"PROPFIND"
    assert ChildView.methods == {"PROPFIND", "GET"}


def test_multiple_inheritance(app, client):
    class GetView(flask.views.MethodView):
        def get(self):
            return "GET"

    class DeleteView(flask.views.MethodView):
        def delete(self):
            return "DELETE"

    class GetDeleteView(GetView, DeleteView):
        pass

    app.add_url_rule("/", view_func=GetDeleteView.as_view("index"))

    assert client.get("/").data == b"GET"
    assert client.delete("/").data == b"DELETE"
    assert sorted(GetDeleteView.methods) == ["DELETE", "GET"]


def test_remove_method_from_parent(app, client):
    class GetView(flask.views.MethodView):
        def get(self):
            return "GET"

    class OtherView(flask.views.MethodView):
        def post(self):
            return "POST"

    class View(GetView, OtherView):
        methods = ["GET"]

    app.add_url_rule("/", view_func=View.as_view("index"))

    assert client.get("/").data == b"GET"
    assert client.post("/").status_code == 405
    assert sorted(View.methods) == ["GET"]
