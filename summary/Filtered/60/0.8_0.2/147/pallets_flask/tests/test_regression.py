import flask


def test_aborting(app):
    """
    This function tests the error handling and redirection mechanism in a Flask application. It sets up an error handler for a custom exception `Foo` and uses it to handle errors raised during route execution. The function includes two routes: one that raises a `flask.abort` with a redirect, and another that raises the `Foo` exception. The test client is used to simulate requests to these routes and verify the expected behavior.
    
    Parameters:
    - app: The Flask application object to which the error handler and routes
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
