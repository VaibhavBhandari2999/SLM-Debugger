import flask


def test_aborting(app):
    """
    This function tests the behavior of error handling and redirection in a Flask application.
    
    Parameters:
    app (Flask): The Flask application to test.
    
    Key Components:
    - `Foo`: A custom exception class used to simulate an error scenario.
    - `handle_foo`: A custom error handler for the `Foo` exception, which returns the value of the `whatever` attribute.
    - `index`: A route that raises a `flask.abort` with a redirect to the 'test'
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
