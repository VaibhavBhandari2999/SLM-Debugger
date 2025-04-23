from io import StringIO

import flask


def test_suppressed_exception_logging():
    """
    Function to test suppressed exception logging in a Flask application.
    
    This function creates a suppressed Flask application and tests whether exceptions are logged or not. The test involves defining a route that raises an exception and then making a request to that route. The function checks the response status and content, as well as the logging output.
    
    Key Parameters:
    - None
    
    Returns:
    - None
    
    Inputs:
    - None
    
    Outputs:
    - None
    
    Keywords:
    - Flask
    - exception
    - logging
    - suppressed
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
