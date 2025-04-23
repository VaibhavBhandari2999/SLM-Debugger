from io import StringIO

import flask


def test_suppressed_exception_logging():
    """
    Function to test suppressed exception logging in a Flask application.
    
    This function creates a suppressed Flask application and tests if exceptions are logged or not. The `SuppressedFlask` class is a subclass of `flask.Flask` that overrides the `log_exception` method to suppress logging of exceptions.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - A `SuppressedFlask` instance is created with the name of the current module.
    - A route `/` is defined with a
    """

    class SuppressedFlask(flask.Flask):
        def log_exception(self, exc_info):
            pass

    out = StringIO()
    app = SuppressedFlask(__name__)

    @app.route("/")
    def index():
        raise Exception("test")

    rv = app.test_client().get("/", errors_stream=out)
    assert rv.status_code == 500
    assert b"Internal Server Error" in rv.data
    assert not out.getvalue()
