import flask


def test_aborting(app):
    """
    This function tests the error handling and redirection mechanism in a Flask application. It sets up an error handler for a custom exception `Foo` and uses `flask.abort` to redirect to a specific route. The function raises a `Foo` exception in the `/test` route and a `flask.abort` in the `/` route, which triggers the error handler.
    
    Key Parameters:
    - `app`: The Flask application object.
    
    The function does not return any value but performs the following actions:
    1
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
