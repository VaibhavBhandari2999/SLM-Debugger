import flask


def test_aborting(app):
    """
    Test aborting in Flask application.
    
    This function tests the behavior of aborting in a Flask application, specifically when an error handler is defined for a custom exception. The function sets up a Flask application with a custom exception handler and two routes. The first route raises a redirect to the second route, which in turn raises the custom exception. The function then makes requests to these routes and checks the response headers and data to ensure the correct behavior.
    
    Parameters:
    app (Flask): The Flask application to
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
