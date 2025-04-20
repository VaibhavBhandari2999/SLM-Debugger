from io import StringIO

import flask


def test_suppressed_exception_logging():
    """
    Function to test exception logging suppression in a Flask application.
    
    This function creates a suppressed exception logging Flask application and tests if exceptions are logged or not. It uses a custom `SuppressedFlask` class that overrides the `log_exception` method to suppress logging of exceptions.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - A `SuppressedFlask` class is defined which inherits from `flask.Flask` and overrides the `log_exception` method to do nothing.
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
