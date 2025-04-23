import flask


def test_aborting(app):
    """
    Test aborting in Flask application.
    
    This function sets up a Flask application with specific error handling and route definitions. It includes an error handler for a custom exception `Foo` and two routes: one that redirects to another route and raises an abort, and another that raises the custom exception `Foo`. The function then tests the behavior of these routes using a test client.
    
    Parameters:
    app (flask.Flask): The Flask application to be tested.
    
    Returns:
    None: This function does not return
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
