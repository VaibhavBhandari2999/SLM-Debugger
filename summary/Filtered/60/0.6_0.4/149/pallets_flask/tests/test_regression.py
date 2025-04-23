import flask


def test_aborting(app):
    """
    Test aborting with error handlers.
    
    This function tests the behavior of aborting with error handlers in a Flask application. It defines a custom exception `Foo` and sets up an error handler for it. The function also defines two routes: one that raises a redirect to another route, and another that raises the custom exception `Foo`. The test client is used to make requests to these routes and verify the expected responses.
    
    Parameters:
    - app: The Flask application to test.
    
    Returns:
    - None: The
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
        location_parts = rv.headers["Location"].rpartition("/")

        if location_parts[0]:
            # For older Werkzeug that used absolute redirects.
            assert location_parts[0] == "http://localhost"

        assert location_parts[2] == "test"
        rv = c.get("/test")
        assert rv.data == b"42"
