import flask


def test_aborting(app):
    """
    Test aborting in Flask application.
    
    This function tests the behavior of aborting in a Flask application. It defines a custom exception `Foo` and a corresponding error handler. It also defines two routes: one that raises a redirect and another that raises the custom exception `Foo`. The function then makes HTTP GET requests to these routes and checks the response headers and data to ensure the expected behavior.
    
    Parameters:
    app (Flask): The Flask application to test.
    
    Returns:
    None: This function does
    """

    class Foo(Exception):
        whatever = 42

    @app.errorhandler(Foo)
    def handle_foo(e):
        return str(e.whatever)

    @app.route("/")
    def index():
        raise flask.abort(flask.redirect(flask.url_for("test")))

    @app.route("/test")
    def test():
        raise Foo()

    with app.test_client() as c:
        rv = c.get("/")
        assert rv.headers["Location"] == "http://localhost/test"
        rv = c.get("/test")
        assert rv.data == b"42"
