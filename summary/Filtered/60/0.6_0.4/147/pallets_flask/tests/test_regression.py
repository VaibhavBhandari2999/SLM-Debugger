import flask


def test_aborting(app):
    """
    Test aborting in a Flask application.
    
    This function sets up a Flask application with specific error handling and routes. It raises an abort with a redirect and a custom exception handler. The function checks the behavior of the application when handling these errors.
    
    Parameters:
    app (Flask): The Flask application to test.
    
    Returns:
    None: The function asserts the expected behavior through test cases.
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
