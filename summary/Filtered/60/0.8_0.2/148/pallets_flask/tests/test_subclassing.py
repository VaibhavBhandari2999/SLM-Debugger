from io import StringIO

import flask


def test_suppressed_exception_logging():
    """
    Function: test_suppressed_exception_logging
    
    This function tests the logging behavior of exceptions in a Flask application when the exception logging is suppressed.
    
    Key Parameters:
    - None
    
    Key Behavior:
    - Creates a custom Flask application that suppresses exception logging.
    - Defines a route that raises an exception.
    - Sends a GET request to the route and captures the response.
    - Verifies that the response status code is 500 (Internal Server Error).
    - Checks that the response data contains the expected error message
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
