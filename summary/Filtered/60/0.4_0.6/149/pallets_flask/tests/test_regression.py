import flask


def test_aborting(app):
    """
    Test aborting in an error handler.
    
    This function tests the behavior of aborting within an error handler in a Flask application. It raises a custom exception and uses an error handler to process it. The function also tests the redirection behavior when aborting with a redirect.
    
    Parameters:
    app (Flask): The Flask application to test.
    
    Returns:
    None: The function asserts the expected behavior and does not return a value.
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
