from io import StringIO

import flask


def test_suppressed_exception_logging():
    """
    Function to test suppressed exception logging in a Flask application.
    
    This function creates a Flask application with a suppressed exception logging mechanism and tests whether an exception is properly handled and logged.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - A custom Flask class `SuppressedFlask` is defined to suppress exception logging.
    - A route `/` is defined that raises an exception.
    - The route is tested using `app.test_client()`.
    - The response status code and data are checked.
    -
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
