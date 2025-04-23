from io import StringIO

import flask


def test_suppressed_exception_logging():
    """
    Function to test suppressed exception logging in a Flask application.
    
    This function creates a suppressed Flask application and tests if exceptions are logged or not. The function sets up a route that raises an exception and checks the response status and content. It also ensures that no exception logs are emitted when the exception is suppressed.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Key Points:
    - A `SuppressedFlask` class is defined to suppress exception logging.
    - A Flask route is defined that raises an exception.
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
