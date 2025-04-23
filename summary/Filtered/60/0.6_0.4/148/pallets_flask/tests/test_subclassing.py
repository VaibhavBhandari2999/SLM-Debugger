from io import StringIO

import flask


def test_suppressed_exception_logging():
    """
    Function to test suppressed exception logging in a Flask application.
    
    This function creates a suppressed Flask application and tests whether exceptions are logged or not. It defines a custom Flask class that suppresses logging of exceptions. The function then sets up a route that raises an exception and makes a GET request to that route. The output is captured to check if the exception is logged.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - A custom Flask class `SuppressedFlask` is defined that
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
