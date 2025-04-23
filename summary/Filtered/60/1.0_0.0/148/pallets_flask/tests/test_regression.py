import flask


def test_aborting(app):
    """
    Test function to handle aborting and error routing in a Flask application.
    
    This function sets up a Flask application with specific error handling and routing. It raises an abort with a redirect and then catches a custom exception to return a specific value. The function tests the behavior of the application when these operations are performed.
    
    Parameters:
    app (Flask): The Flask application to configure and test.
    
    Returns:
    None: This function does not return a value. It performs the test within the function body.
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
