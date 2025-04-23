import pytest
from werkzeug.http import parse_set_header

import flask.views


def common_test(app):
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
    """
    This function tests the behavior of view patching in a Flask application. It involves creating a custom view class with specific methods and then patching the view class at runtime to change its behavior. The function sets up a Flask application with a URL rule that maps to the patched view and then runs common tests on the application.
    
    Key Parameters:
    - app: The Flask application instance to which the view is added.
    
    Input:
    - A Flask application instance.
    
    Output:
    - The function does not return any value but
    """

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
    """
    Tests the inheritance of methods and variables in a Flask application. The function sets up a Flask application with a base view and a child view. The base view defines the methods 'GET' and 'PROPFIND'. The child view inherits from the base view and implements the 'get' and 'propfind' methods. The function then adds a URL rule for the child view and uses a client to make GET and PROPFIND requests to the root URL. The function asserts that the correct responses are
    """

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
