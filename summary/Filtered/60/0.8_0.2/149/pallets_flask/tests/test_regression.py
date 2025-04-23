import flask


def test_aborting(app):
    """
    Test function to handle aborting and error handling in a Flask application.
    
    This function sets up a Flask application with specific error handlers and routes. It then tests the behavior when an abort is called, which in turn raises a custom exception. The function checks that the redirect is handled correctly and that the custom exception is caught and handled by the error handler.
    
    Parameters:
    app (Flask): The Flask application to configure and test.
    
    Returns:
    None: The function asserts the correctness of the application's
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
